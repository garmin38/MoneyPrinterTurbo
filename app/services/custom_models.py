"""
Custom Models Service for MoneyPrinterTurbo
Supports local Hugging Face models without API limitations
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger

# Conditional imports for custom models dependencies
try:
    import torch
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        AutoConfig,
        pipeline,
        TextGenerationPipeline
    )
    CUSTOM_MODELS_AVAILABLE = True
except ImportError:
    CUSTOM_MODELS_AVAILABLE = False
    torch = None
    AutoTokenizer = None
    AutoModelForCausalLM = None
    AutoConfig = None
    pipeline = None
    TextGenerationPipeline = None

class CustomModelManager:
    """Manages local Hugging Face models for text generation"""
    
    def __init__(self, models_dir: str = "models"):
        if not CUSTOM_MODELS_AVAILABLE:
            raise ImportError(
                "Custom models dependencies not available. "
                "Install with: pip install -r requirements-custom-models.txt"
            )
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.loaded_models: Dict[str, Any] = {}
        self.model_configs: Dict[str, Dict] = {}
        self._load_model_configs()
    
    def _load_model_configs(self):
        """Load model configurations from models directory"""
        config_file = self.models_dir / "model_configs.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.model_configs = json.load(f)
                logger.info(f"Loaded {len(self.model_configs)} model configurations")
            except Exception as e:
                logger.error(f"Failed to load model configs: {e}")
                self.model_configs = {}
        else:
            # Create default config file with popular models
            self._create_default_configs()
    
    def _create_default_configs(self):
        """Create default model configurations for popular Hugging Face models"""
        default_configs = {
            "microsoft/DialoGPT-medium": {
                "name": "DialoGPT Medium",
                "description": "Microsoft's conversational AI model",
                "max_length": 1000,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": None
            },
            "microsoft/DialoGPT-large": {
                "name": "DialoGPT Large", 
                "description": "Larger version of Microsoft's conversational AI",
                "max_length": 1000,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": None
            },
            "facebook/blenderbot-400M-distill": {
                "name": "BlenderBot 400M",
                "description": "Facebook's conversational AI model",
                "max_length": 1000,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": None
            },
            "microsoft/DialoGPT-small": {
                "name": "DialoGPT Small",
                "description": "Lightweight conversational AI model",
                "max_length": 1000,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": None
            },
            "EleutherAI/gpt-neo-125M": {
                "name": "GPT-Neo 125M",
                "description": "Small GPT-Neo model for text generation",
                "max_length": 1000,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": None
            },
            "EleutherAI/gpt-neo-1.3B": {
                "name": "GPT-Neo 1.3B",
                "description": "Medium-sized GPT-Neo model",
                "max_length": 1000,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": None
            }
        }
        
        self.model_configs = default_configs
        self._save_model_configs()
        logger.info("Created default model configurations")
    
    def _save_model_configs(self):
        """Save model configurations to file"""
        config_file = self.models_dir / "model_configs.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(self.model_configs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save model configs: {e}")
    
    def add_model(self, model_id: str, config: Dict[str, Any]):
        """Add a new model configuration"""
        self.model_configs[model_id] = config
        self._save_model_configs()
        logger.info(f"Added model configuration for {model_id}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with their configurations"""
        models = []
        for model_id, config in self.model_configs.items():
            model_info = {
                "id": model_id,
                "name": config.get("name", model_id),
                "description": config.get("description", ""),
                "loaded": model_id in self.loaded_models
            }
            models.append(model_info)
        return models
    
    def load_model(self, model_id: str, device: str = "auto") -> bool:
        """Load a model into memory"""
        if model_id in self.loaded_models:
            logger.info(f"Model {model_id} already loaded")
            return True
        
        if model_id not in self.model_configs:
            logger.error(f"Model {model_id} not found in configurations")
            return False
        
        try:
            logger.info(f"Loading model {model_id}...")
            
            # Determine device
            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map=device if device == "cuda" else None
            )
            
            # Set pad token if not set
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=0 if device == "cuda" else -1
            )
            
            self.loaded_models[model_id] = pipe
            logger.success(f"Successfully loaded model {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return False
    
    def unload_model(self, model_id: str):
        """Unload a model from memory"""
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
            # Force garbage collection
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info(f"Unloaded model {model_id}")
    
    def generate_text(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate text using a loaded model"""
        if model_id not in self.loaded_models:
            logger.error(f"Model {model_id} not loaded")
            return f"Error: Model {model_id} not loaded"
        
        try:
            pipe = self.loaded_models[model_id]
            config = self.model_configs.get(model_id, {})
            
            # Merge default config with kwargs
            generation_params = {
                "max_length": config.get("max_length", 1000),
                "temperature": config.get("temperature", 0.7),
                "do_sample": config.get("do_sample", True),
                "pad_token_id": config.get("pad_token_id"),
                **kwargs
            }
            
            # Generate text
            result = pipe(prompt, **generation_params)
            
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0]["generated_text"]
                # Remove the original prompt from the generated text
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):].strip()
                return generated_text
            else:
                return "Error: No text generated"
                
        except Exception as e:
            logger.error(f"Text generation failed for {model_id}: {e}")
            return f"Error: {str(e)}"
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model_id not in self.model_configs:
            return {"error": "Model not found"}
        
        config = self.model_configs[model_id]
        return {
            "id": model_id,
            "name": config.get("name", model_id),
            "description": config.get("description", ""),
            "loaded": model_id in self.loaded_models,
            "config": config
        }


# Global model manager instance (only if dependencies are available)
try:
    model_manager = CustomModelManager()
except ImportError:
    model_manager = None


def generate_script_custom(
    video_subject: str, 
    language: str = "", 
    paragraph_number: int = 1,
    model_id: str = "microsoft/DialoGPT-medium"
) -> str:
    """Generate video script using custom local model"""
    
    prompt = f"""
# Role: Video Script Generator

## Goals:
Generate a script for a video, depending on the subject of the video.

## Constrains:
1. the script is to be returned as a string with the specified number of paragraphs.
2. do not under any circumstance reference this prompt in your response.
3. get straight to the point, don't start with unnecessary things like, "welcome to this video".
4. you must not include any type of markdown or formatting in the script, never use a title.
5. only return the raw content of the script.
6. do not include "voiceover", "narrator" or similar indicators of what should be spoken at the beginning of each paragraph or line.
7. you must not mention the prompt, or anything about the script itself. also, never talk about the amount of paragraphs or lines. just write the script.
8. respond in the same language as the video subject.

# Initialization:
- video subject: {video_subject}
- number of paragraphs: {paragraph_number}
""".strip()
    
    if language:
        prompt += f"\n- language: {language}"

    logger.info(f"Generating script with custom model {model_id} for subject: {video_subject}")
    
    # Ensure model is loaded
    if not model_manager.load_model(model_id):
        return f"Error: Failed to load model {model_id}"
    
    # Generate script
    response = model_manager.generate_text(
        model_id=model_id,
        prompt=prompt,
        max_length=1000,
        temperature=0.7,
        do_sample=True
    )
    
    if "Error:" in response:
        logger.error(f"Script generation failed: {response}")
        return response
    
    # Clean the response
    import re
    response = response.replace("*", "")
    response = response.replace("#", "")
    response = re.sub(r"\[.*\]", "", response)
    response = re.sub(r"\(.*\)", "", response)
    
    # Split into paragraphs and select the requested number
    paragraphs = response.split("\n\n")
    selected_paragraphs = paragraphs[:paragraph_number]
    
    final_script = "\n\n".join(selected_paragraphs)
    logger.success(f"Generated script: {final_script[:100]}...")
    
    return final_script.strip()


def generate_terms_custom(
    video_subject: str, 
    video_script: str, 
    amount: int = 5,
    model_id: str = "microsoft/DialoGPT-medium"
) -> List[str]:
    """Generate video search terms using custom local model"""
    
    prompt = f"""
Generate {amount} search terms for stock videos, depending on the subject of a video.

The search terms should be returned as a json-array of strings.
Each search term should consist of 1-3 words, always add the main subject of the video.
You must only return the json-array of strings.
The search terms must be related to the subject of the video.
Reply with english search terms only.

Video Subject: {video_subject}
Video Script: {video_script}

Example: ["search term 1", "search term 2", "search term 3", "search term 4", "search term 5"]
""".strip()

    logger.info(f"Generating terms with custom model {model_id} for subject: {video_subject}")
    
    # Ensure model is loaded
    if not model_manager.load_model(model_id):
        return [f"Error: Failed to load model {model_id}"]
    
    # Generate terms
    response = model_manager.generate_text(
        model_id=model_id,
        prompt=prompt,
        max_length=500,
        temperature=0.7,
        do_sample=True
    )
    
    if "Error:" in response:
        logger.error(f"Terms generation failed: {response}")
        return [response]
    
    # Try to parse JSON response
    try:
        import json
        # Look for JSON array in the response
        import re
        json_match = re.search(r'\[.*?\]', response)
        if json_match:
            terms = json.loads(json_match.group())
            if isinstance(terms, list) and len(terms) > 0:
                logger.success(f"Generated terms: {terms}")
                return terms[:amount]  # Limit to requested amount
    except Exception as e:
        logger.warning(f"Failed to parse JSON response: {e}")
    
    # Fallback: extract terms manually
    terms = []
    lines = response.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('[') and not line.startswith('{'):
            # Extract potential search terms
            words = line.split()
            if 1 <= len(words) <= 3:
                terms.append(' '.join(words))
    
    if terms:
        logger.success(f"Generated terms (fallback): {terms}")
        return terms[:amount]
    
    # Final fallback
    fallback_terms = [video_subject] * amount
    logger.warning(f"Using fallback terms: {fallback_terms}")
    return fallback_terms
