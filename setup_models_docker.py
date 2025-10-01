#!/usr/bin/env python3
"""
Setup script for downloading Hugging Face models in Docker environment
This script can be run inside the Docker container to download models
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        print("✅ Custom models dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Custom models dependencies not available: {e}")
        print("Please ensure the Docker image was built with custom models support")
        return False

def download_model(model_id: str, models_dir: str = "/MoneyPrinterTurbo/models") -> bool:
    """Download a specific model from Hugging Face"""
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print(f"📥 Downloading model: {model_id}")
        
        # Create models directory
        Path(models_dir).mkdir(parents=True, exist_ok=True)
        
        # Download tokenizer
        print(f"   📥 Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            cache_dir=models_dir
        )
        
        # Download model
        print(f"   📥 Downloading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            cache_dir=models_dir,
            torch_dtype="auto"
        )
        
        print(f"✅ Successfully downloaded {model_id}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {model_id}: {e}")
        return False

def download_recommended_models(models_dir: str = "/MoneyPrinterTurbo/models") -> List[str]:
    """Download recommended models for MoneyPrinterTurbo"""
    
    recommended_models = [
        {
            "id": "microsoft/DialoGPT-medium",
            "name": "DialoGPT Medium ⭐ RECOMMENDED",
            "description": "Best balance of quality and performance (345M parameters)",
            "size": "~1.4GB"
        },
        {
            "id": "microsoft/DialoGPT-small", 
            "name": "DialoGPT Small",
            "description": "Lightweight for testing (117M parameters)",
            "size": "~500MB"
        }
    ]
    
    print("🚀 Downloading recommended models for MoneyPrinterTurbo")
    print("=" * 60)
    
    downloaded_models = []
    
    for model_info in recommended_models:
        print(f"\n📥 {model_info['name']}")
        print(f"   Description: {model_info['description']}")
        print(f"   Size: {model_info['size']}")
        
        if download_model(model_info['id'], models_dir):
            downloaded_models.append(model_info['id'])
        else:
            print(f"   ⚠️  Skipping {model_info['id']} due to download failure")
    
    return downloaded_models

def create_model_configs(models_dir: str = "/MoneyPrinterTurbo/models"):
    """Create model configuration file"""
    config_file = Path(models_dir) / "model_configs.json"
    
    default_configs = {
        "microsoft/DialoGPT-small": {
            "name": "DialoGPT Small",
            "description": "Lightweight conversational AI model (117M parameters)",
            "max_length": 1000,
            "temperature": 0.7,
            "do_sample": True,
            "pad_token_id": None,
            "use_case": "conversational",
            "size": "~500MB"
        },
        "microsoft/DialoGPT-medium": {
            "name": "DialoGPT Medium",
            "description": "Medium conversational AI model (345M parameters)",
            "max_length": 1000,
            "temperature": 0.7,
            "do_sample": True,
            "pad_token_id": None,
            "use_case": "conversational",
            "size": "~1.4GB"
        },
        "microsoft/DialoGPT-large": {
            "name": "DialoGPT Large",
            "description": "Large conversational AI model (774M parameters)",
            "max_length": 1000,
            "temperature": 0.7,
            "do_sample": True,
            "pad_token_id": None,
            "use_case": "conversational",
            "size": "~3.1GB"
        },
        "facebook/blenderbot-400M-distill": {
            "name": "BlenderBot 400M",
            "description": "Facebook's conversational AI model (400M parameters)",
            "max_length": 1000,
            "temperature": 0.7,
            "do_sample": True,
            "pad_token_id": None,
            "use_case": "conversational",
            "size": "~1.6GB"
        }
    }
    
    try:
        with open(config_file, 'w') as f:
            json.dump(default_configs, f, indent=2)
        print(f"✅ Created model configurations: {config_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create model configs: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Setup Hugging Face models for MoneyPrinterTurbo")
    parser.add_argument("--models-dir", default="/MoneyPrinterTurbo/models", 
                       help="Directory to store models")
    parser.add_argument("--model-id", help="Download specific model ID")
    parser.add_argument("--recommended", action="store_true", 
                       help="Download recommended models")
    parser.add_argument("--check-only", action="store_true",
                       help="Only check if dependencies are available")
    
    args = parser.parse_args()
    
    print("🚀 MoneyPrinterTurbo Custom Models Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 To fix this issue:")
        print("1. Rebuild the Docker image with custom models support")
        print("2. Or use external APIs instead of custom models")
        return 1
    
    if args.check_only:
        print("✅ Dependencies check passed")
        return 0
    
    # Create models directory
    Path(args.models_dir).mkdir(parents=True, exist_ok=True)
    
    # Create model configurations
    create_model_configs(args.models_dir)
    
    # Download models
    if args.model_id:
        # Download specific model
        print(f"\n📥 Downloading specific model: {args.model_id}")
        if download_model(args.model_id, args.models_dir):
            print(f"✅ Successfully downloaded {args.model_id}")
        else:
            print(f"❌ Failed to download {args.model_id}")
            return 1
    elif args.recommended:
        # Download recommended models
        downloaded = download_recommended_models(args.models_dir)
        print(f"\n🎉 Downloaded {len(downloaded)} models:")
        for model_id in downloaded:
            print(f"   ✅ {model_id}")
    else:
        print("\n💡 Usage:")
        print("   --recommended     Download recommended models")
        print("   --model-id ID     Download specific model")
        print("   --check-only      Check dependencies only")
        return 0
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Restart MoneyPrinterTurbo if it's running")
    print("2. Configure custom models in the WebUI")
    print("3. Select 'Custom' as LLM Provider")
    print("4. Set your preferred model ID")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
