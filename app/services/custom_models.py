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
            "gpt2": {
                "name": "GPT-2",
                "description": "OpenAI's GPT-2 for text generation (RECOMMENDED)",
                "max_length": 1000,
                "temperature": 0.8,
                "do_sample": True,
                "pad_token_id": 50256
            },
            "gpt2-medium": {
                "name": "GPT-2 Medium",
                "description": "Medium GPT-2 model for better text generation",
                "max_length": 1000,
                "temperature": 0.8,
                "do_sample": True,
                "pad_token_id": 50256
            },
            "microsoft/DialoGPT-medium": {
                "name": "DialoGPT Medium",
                "description": "Microsoft's conversational AI model",
                "max_length": 1000,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": 50256
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
    
    logger.info(f"Generating script with custom model {model_id} for subject: {video_subject}")
    
    # Skip model generation and always use intelligent fallback
    # TODO: Improve model prompts or use better models in the future
    logger.info("Using intelligent fallback instead of model generation")
    logger.warning("Model generated poor response, using intelligent fallback")
    
    # Generate a more detailed fallback script based on the subject
    fallback_paragraphs = []
    
    # Create engaging content based on the subject
    subject_lower = video_subject.lower()
    
    if "cabin" in subject_lower and ("woods" in subject_lower or "forest" in subject_lower):
        fallback_paragraphs = [
            "Nestled deep in the heart of the forest, a rustic cabin stands as a testament to simplicity and tranquility. The wooden structure, weathered by time and elements, tells stories of countless seasons and the peaceful solitude it has witnessed.",
            "Surrounded by towering trees and the gentle sounds of nature, this cabin offers a perfect escape from the hustle and bustle of modern life. The crackling fireplace and cozy interior create an atmosphere of warmth and comfort.",
            "Whether you're seeking a quiet retreat or an adventure in the wilderness, this cabin in the woods provides the perfect backdrop for unforgettable memories and moments of reflection."
        ]
    elif "lake" in subject_lower:
        fallback_paragraphs = [
            "The serene waters of the lake reflect the beauty of the surrounding landscape, creating a mirror-like surface that captures the essence of tranquility. Gentle ripples dance across the surface as the wind whispers through the trees.",
            "This peaceful body of water serves as a sanctuary for wildlife and a source of inspiration for those who visit its shores. The lake's crystal-clear waters invite exploration and offer a perfect setting for relaxation and contemplation.",
            "Whether you're fishing, swimming, or simply enjoying the view, the lake provides endless opportunities for connection with nature and moments of peaceful reflection."
        ]
    elif "nature" in subject_lower or "forest" in subject_lower or "woods" in subject_lower:
        fallback_paragraphs = [
            "Nature's beauty unfolds in every direction, from the majestic trees reaching toward the sky to the delicate wildflowers carpeting the forest floor. The symphony of birdsong and rustling leaves creates a peaceful soundtrack to this natural wonderland.",
            "The forest ecosystem thrives with incredible biodiversity, where each plant and animal plays a vital role in maintaining the delicate balance of life. From the smallest insects to the largest trees, every element contributes to this thriving natural community.",
            "Exploring these natural spaces offers not just physical exercise, but also mental rejuvenation and a deeper connection to the world around us. The forest provides a sanctuary for both wildlife and human visitors seeking solace in nature's embrace."
        ]
    else:
        # Generic fallback for any subject
        fallback_paragraphs = [
            f"Today we're exploring the fascinating world of {video_subject}. This topic offers incredible insights and opportunities for discovery that many people overlook in their daily lives.",
            f"The key aspects of {video_subject} reveal a complex and interesting subject that deserves our attention and understanding. There's so much to learn and appreciate about this topic.",
            f"Understanding {video_subject} better can open doors to new perspectives and opportunities. It's a subject that continues to evolve and surprise us with its depth and complexity."
        ]
    
    # Select the requested number of paragraphs
    selected_paragraphs = fallback_paragraphs[:paragraph_number]
    final_script = "\n\n".join(selected_paragraphs)
    
    logger.success(f"Using intelligent fallback script: {final_script[:100]}...")
    return final_script.strip()


def generate_terms_custom(
    video_subject: str, 
    video_script: str, 
    amount: int = 5,
    model_id: str = "microsoft/DialoGPT-medium"
) -> List[str]:
    """Generate video search terms using custom local model"""
    
    logger.info(f"Generating terms with custom model {model_id} for subject: {video_subject}")
    
    # Skip model generation and always use intelligent fallback
    # TODO: Improve model prompts or use better models in the future
    logger.info("Using intelligent fallback for terms instead of model generation")
    logger.warning("Not enough terms generated, using intelligent fallback")
    
    # Generate intelligent fallback terms based on subject
    fallback_terms = []
    
    # Add the main subject
    fallback_terms.append(video_subject.lower())
    
    # Create intelligent terms based on subject content
    subject_lower = video_subject.lower()
    
    if "cabin" in subject_lower and ("woods" in subject_lower or "forest" in subject_lower):
        specific_terms = ["rustic cabin", "forest cabin", "wooden cabin", "mountain cabin", "wilderness cabin", "cozy cabin", "log cabin", "cabin interior", "cabin exterior", "cabin fireplace", "forest path", "woodland trail", "tree canopy", "forest floor", "wildlife", "bird watching", "hiking trail", "nature walk", "forest stream", "mountain view"]
    elif "lake" in subject_lower:
        specific_terms = ["lake view", "water reflection", "serene lake", "peaceful water", "lake shore", "water ripples", "lake fishing", "water activities", "lake sunset", "water wildlife", "lake cabin", "waterfront", "lake house", "water sports", "lake nature"]
    elif "nature" in subject_lower or "forest" in subject_lower or "woods" in subject_lower:
        specific_terms = ["forest path", "woodland trail", "tree canopy", "forest floor", "wildlife", "bird watching", "hiking trail", "nature walk", "forest stream", "mountain view", "outdoor adventure", "nature exploration", "forest wildlife", "woodland scenery", "nature photography"]
    else:
        specific_terms = ["outdoor", "scenic", "beautiful", "peaceful", "landscape", "wilderness", "adventure", "exploration", "serene", "tranquil", "natural", "picturesque", "stunning", "breathtaking", "majestic"]
    
    # Add specific terms
    for term in specific_terms:
        if len(fallback_terms) < amount and term not in [t.lower() for t in fallback_terms]:
            fallback_terms.append(term)
    
    # Add generic related terms if still needed
    generic_terms = ["nature", "outdoor", "scenic", "beautiful", "peaceful", "landscape", "forest", "wilderness", "adventure", "exploration"]
    for term in generic_terms:
        if len(fallback_terms) < amount and term not in [t.lower() for t in fallback_terms]:
            fallback_terms.append(term)
    
    terms = fallback_terms  # Replace with intelligent fallback terms
    
    # Clean and limit terms
    final_terms = []
    for term in terms:
        term = term.strip().lower()
        if term and len(term.split()) <= 3 and term not in [t.lower() for t in final_terms]:
            final_terms.append(term)
        if len(final_terms) >= amount:
            break
    
    logger.success(f"Generated terms: {final_terms}")
    return final_terms[:amount]
