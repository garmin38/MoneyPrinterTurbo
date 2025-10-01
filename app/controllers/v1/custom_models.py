"""
Custom Models API Controller
Provides endpoints for managing and using local Hugging Face models
"""

from fastapi import Request, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.controllers.v1.base import new_router
from app.utils import utils

# Conditional imports for custom models
try:
    from app.services.custom_models import model_manager, generate_script_custom, generate_terms_custom
    CUSTOM_MODELS_AVAILABLE = True
except ImportError:
    CUSTOM_MODELS_AVAILABLE = False
    model_manager = None
    generate_script_custom = None
    generate_terms_custom = None

router = new_router()


def check_custom_models_available():
    """Check if custom models are available, raise HTTPException if not"""
    if not CUSTOM_MODELS_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Custom models not available. Install dependencies: pip install -r requirements-custom-models.txt"
        )


class ModelInfo(BaseModel):
    id: str
    name: str
    description: str
    loaded: bool


class ModelConfig(BaseModel):
    name: str
    description: str
    max_length: int = 1000
    temperature: float = 0.7
    do_sample: bool = True
    pad_token_id: Optional[int] = None


class LoadModelRequest(BaseModel):
    model_id: str
    device: str = "auto"


class GenerateScriptRequest(BaseModel):
    video_subject: str
    language: str = ""
    paragraph_number: int = 1
    model_id: str = "microsoft/DialoGPT-medium"


class GenerateTermsRequest(BaseModel):
    video_subject: str
    video_script: str
    amount: int = 5
    model_id: str = "microsoft/DialoGPT-medium"


@router.get(
    "/models",
    response_model=List[ModelInfo],
    summary="Get list of available custom models"
)
def get_available_models(request: Request):
    """Get list of all available custom models"""
    check_custom_models_available()
    try:
        models = model_manager.get_available_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@router.get(
    "/models/{model_id}",
    response_model=Dict[str, Any],
    summary="Get information about a specific model"
)
def get_model_info(request: Request, model_id: str):
    """Get detailed information about a specific model"""
    check_custom_models_available()
    try:
        info = model_manager.get_model_info(model_id)
        if "error" in info:
            raise HTTPException(status_code=404, detail=info["error"])
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")


@router.post(
    "/models/{model_id}/load",
    summary="Load a model into memory"
)
def load_model(request: Request, model_id: str, body: LoadModelRequest):
    """Load a specific model into memory for use"""
    check_custom_models_available()
    try:
        success = model_manager.load_model(model_id, body.device)
        if success:
            return utils.get_response(200, {"message": f"Model {model_id} loaded successfully"})
        else:
            raise HTTPException(status_code=400, detail=f"Failed to load model {model_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@router.delete(
    "/models/{model_id}/unload",
    summary="Unload a model from memory"
)
def unload_model(request: Request, model_id: str):
    """Unload a model from memory to free up resources"""
    check_custom_models_available()
    try:
        model_manager.unload_model(model_id)
        return utils.get_response(200, {"message": f"Model {model_id} unloaded successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unload model: {str(e)}")


@router.post(
    "/models/{model_id}/config",
    summary="Update model configuration"
)
def update_model_config(request: Request, model_id: str, config: ModelConfig):
    """Update configuration for a specific model"""
    check_custom_models_available()
    try:
        config_dict = config.dict()
        model_manager.add_model(model_id, config_dict)
        return utils.get_response(200, {"message": f"Configuration updated for model {model_id}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update model config: {str(e)}")


@router.post(
    "/scripts",
    summary="Generate video script using custom model"
)
def generate_video_script(request: Request, body: GenerateScriptRequest):
    """Generate a video script using a custom local model"""
    check_custom_models_available()
    try:
        script = generate_script_custom(
            video_subject=body.video_subject,
            language=body.language,
            paragraph_number=body.paragraph_number,
            model_id=body.model_id
        )
        
        if script.startswith("Error:"):
            raise HTTPException(status_code=400, detail=script)
        
        return utils.get_response(200, {"video_script": script})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")


@router.post(
    "/terms",
    summary="Generate video search terms using custom model"
)
def generate_video_terms(request: Request, body: GenerateTermsRequest):
    """Generate video search terms using a custom local model"""
    check_custom_models_available()
    try:
        terms = generate_terms_custom(
            video_subject=body.video_subject,
            video_script=body.video_script,
            amount=body.amount,
            model_id=body.model_id
        )
        
        if terms and terms[0].startswith("Error:"):
            raise HTTPException(status_code=400, detail=terms[0])
        
        return utils.get_response(200, {"video_terms": terms})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate terms: {str(e)}")


@router.post(
    "/models/{model_id}/generate",
    summary="Generate text using a specific model"
)
def generate_text(request: Request, model_id: str, body: Dict[str, Any]):
    """Generate text using a specific loaded model"""
    check_custom_models_available()
    try:
        prompt = body.get("prompt", "")
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Remove prompt from body for generation parameters
        generation_params = {k: v for k, v in body.items() if k != "prompt"}
        
        response = model_manager.generate_text(model_id, prompt, **generation_params)
        
        if response.startswith("Error:"):
            raise HTTPException(status_code=400, detail=response)
        
        return utils.get_response(200, {"generated_text": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate text: {str(e)}")
