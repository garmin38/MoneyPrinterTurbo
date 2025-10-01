#!/usr/bin/env python3
"""
Setup script for MoneyPrinterTurbo Custom Models
Downloads and configures popular Hugging Face models for local use
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

def create_models_directory():
    """Create the models directory structure"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Create subdirectories for different model types
    (models_dir / "text_generation").mkdir(exist_ok=True)
    (models_dir / "conversational").mkdir(exist_ok=True)
    (models_dir / "summarization").mkdir(exist_ok=True)
    
    print(f"✅ Created models directory: {models_dir.absolute()}")
    return models_dir

def download_popular_models():
    """Download popular models for different use cases"""
    from transformers import AutoTokenizer, AutoModelForCausalLM
    
    models_to_download = [
        {
            "id": "microsoft/DialoGPT-medium", 
            "name": "DialoGPT Medium ⭐ RECOMMENDED",
            "description": "Best balance of quality and performance (345M parameters)",
            "size": "~1.4GB",
            "use_case": "conversational",
            "priority": "high"
        },
        {
            "id": "microsoft/DialoGPT-small",
            "name": "DialoGPT Small",
            "description": "Lightweight for testing and quick generation (117M parameters)",
            "size": "~500MB",
            "use_case": "conversational",
            "priority": "medium"
        },
        {
            "id": "facebook/blenderbot-400M-distill",
            "name": "BlenderBot 400M",
            "description": "Excellent for conversational and educational content (400M parameters)",
            "size": "~1.6GB", 
            "use_case": "conversational",
            "priority": "medium"
        },
        {
            "id": "EleutherAI/gpt-neo-125M",
            "name": "GPT-Neo 125M",
            "description": "Great for creative and diverse content (125M parameters)",
            "size": "~500MB",
            "use_case": "text_generation",
            "priority": "low"
        }
    ]
    
    print("🚀 Starting model downloads...")
    print("This may take a while depending on your internet connection.")
    print("Models will be cached locally for future use.\n")
    
    # Sort by priority (high first)
    models_to_download.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])
    
    for model_info in models_to_download:
        model_id = model_info["id"]
        print(f"📥 Downloading {model_info['name']} ({model_info['size']})...")
        
        try:
            # Download tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            
            # Download model
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype="auto"
            )
            
            print(f"✅ Successfully downloaded {model_info['name']}")
            
        except Exception as e:
            print(f"❌ Failed to download {model_info['name']}: {e}")
            continue
    
    print("\n🎉 Model download process completed!")

def create_model_configs():
    """Create configuration file for downloaded models"""
    models_dir = Path("models")
    config_file = models_dir / "model_configs.json"
    
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
        },
        "EleutherAI/gpt-neo-125M": {
            "name": "GPT-Neo 125M",
            "description": "Small GPT-Neo model for text generation (125M parameters)",
            "max_length": 1000,
            "temperature": 0.7,
            "do_sample": True,
            "pad_token_id": None,
            "use_case": "text_generation",
            "size": "~500MB"
        },
        "EleutherAI/gpt-neo-1.3B": {
            "name": "GPT-Neo 1.3B",
            "description": "Medium-sized GPT-Neo model (1.3B parameters)",
            "max_length": 1000,
            "temperature": 0.7,
            "do_sample": True,
            "pad_token_id": None,
            "use_case": "text_generation",
            "size": "~5.2GB"
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(default_configs, f, indent=2)
    
    print(f"✅ Created model configurations: {config_file}")

def update_config_toml():
    """Update config.toml to include custom models settings"""
    config_file = Path("config.toml")
    
    if not config_file.exists():
        print("⚠️  config.toml not found. Please run the application first to create it.")
        return
    
    # Read current config
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Add custom models section if not present
    if "custom_model_id" not in content:
        custom_section = """
########## Custom Models (Local Hugging Face Models)
# Use local Hugging Face models without API limitations
# Popular models: microsoft/DialoGPT-medium, microsoft/DialoGPT-large, facebook/blenderbot-400M-distill
custom_model_id = "microsoft/DialoGPT-medium"
# Device to run models on: "auto", "cpu", "cuda"
custom_model_device = "auto"
"""
        
        # Insert before the first [section]
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('[') and not line.startswith('[app]'):
                insert_index = i
                break
        
        lines.insert(insert_index, custom_section)
        
        with open(config_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ Updated config.toml with custom models settings")
    else:
        print("✅ config.toml already contains custom models settings")

def print_usage_instructions():
    """Print instructions for using custom models"""
    print("\n" + "="*60)
    print("🎉 Custom Models Setup Complete!")
    print("="*60)
    print("\n📋 How to use custom models:")
    print("1. Set llm_provider = 'custom' in your config.toml")
    print("2. Set custom_model_id to your preferred model")
    print("3. Restart the MoneyPrinterTurbo application")
    print("\n🔧 Available models:")
    print("   • microsoft/DialoGPT-small (117M params, ~500MB)")
    print("   • microsoft/DialoGPT-medium (345M params, ~1.4GB)")  
    print("   • microsoft/DialoGPT-large (774M params, ~3.1GB)")
    print("   • facebook/blenderbot-400M-distill (400M params, ~1.6GB)")
    print("   • EleutherAI/gpt-neo-125M (125M params, ~500MB)")
    print("   • EleutherAI/gpt-neo-1.3B (1.3B params, ~5.2GB)")
    print("\n🌐 API Endpoints:")
    print("   • GET /custom-models/models - List available models")
    print("   • POST /custom-models/models/{model_id}/load - Load a model")
    print("   • POST /custom-models/scripts - Generate script with custom model")
    print("   • POST /custom-models/terms - Generate terms with custom model")
    print("\n💡 Tips:")
    print("   • Start with smaller models (DialoGPT-small) for testing")
    print("   • Use GPU if available for better performance")
    print("   • Models are cached locally after first download")
    print("   • Check /docs for full API documentation")
    print("\n" + "="*60)

def main():
    parser = argparse.ArgumentParser(description="Setup MoneyPrinterTurbo Custom Models")
    parser.add_argument("--download", action="store_true", help="Download popular models")
    parser.add_argument("--config-only", action="store_true", help="Only create configurations")
    parser.add_argument("--skip-download", action="store_true", help="Skip model downloads")
    
    args = parser.parse_args()
    
    print("🚀 MoneyPrinterTurbo Custom Models Setup")
    print("="*50)
    
    # Create directory structure
    create_models_directory()
    
    # Create model configurations
    create_model_configs()
    
    # Update config.toml
    update_config_toml()
    
    # Download models if requested
    if args.download or (not args.config_only and not args.skip_download):
        try:
            download_popular_models()
        except ImportError:
            print("❌ transformers library not found. Please install requirements:")
            print("   pip install -r requirements-custom-models.txt")
            return
        except Exception as e:
            print(f"❌ Error during model download: {e}")
            print("   You can download models later using the API")
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    main()
