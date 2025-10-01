#!/usr/bin/env python3
"""
Demo script for MoneyPrinterTurbo Custom Models
Shows how to use local Hugging Face models for video generation
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://127.0.0.1:8080"
CUSTOM_MODELS_URL = f"{BASE_URL}/custom-models"

def test_model_management():
    """Test model management endpoints"""
    print("🔧 Testing Model Management")
    print("=" * 40)
    
    # List available models
    print("📋 Listing available models...")
    response = requests.get(f"{CUSTOM_MODELS_URL}/models")
    if response.status_code == 200:
        models = response.json()
        print(f"✅ Found {len(models)} models:")
        for model in models:
            status = "🟢 Loaded" if model['loaded'] else "🔴 Not loaded"
            print(f"   • {model['name']} ({model['id']}) - {status}")
    else:
        print(f"❌ Failed to list models: {response.text}")
        return False
    
    # Load a model
    print("\n📥 Loading DialoGPT-medium...")
    load_data = {"device": "auto"}
    response = requests.post(
        f"{CUSTOM_MODELS_URL}/models/microsoft/DialoGPT-medium/load",
        json=load_data
    )
    if response.status_code == 200:
        print("✅ Model loaded successfully")
    else:
        print(f"❌ Failed to load model: {response.text}")
        return False
    
    return True

def test_script_generation():
    """Test video script generation"""
    print("\n🎬 Testing Script Generation")
    print("=" * 40)
    
    test_cases = [
        {
            "video_subject": "The benefits of regular exercise",
            "language": "en",
            "paragraph_number": 1,
            "model_id": "microsoft/DialoGPT-medium"
        },
        {
            "video_subject": "如何学习编程",
            "language": "zh-CN", 
            "paragraph_number": 1,
            "model_id": "microsoft/DialoGPT-medium"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['video_subject']}")
        
        response = requests.post(
            f"{CUSTOM_MODELS_URL}/scripts",
            json=test_case
        )
        
        if response.status_code == 200:
            result = response.json()
            script = result.get('video_script', '')
            print(f"✅ Generated script ({len(script)} chars):")
            print(f"   {script[:100]}...")
        else:
            print(f"❌ Failed to generate script: {response.text}")

def test_terms_generation():
    """Test video search terms generation"""
    print("\n🔍 Testing Terms Generation")
    print("=" * 40)
    
    test_case = {
        "video_subject": "The benefits of regular exercise",
        "video_script": "Exercise is one of the most important things you can do for your health. Regular physical activity can help you maintain a healthy weight, reduce your risk of chronic diseases, and improve your mental health.",
        "amount": 5,
        "model_id": "microsoft/DialoGPT-medium"
    }
    
    print(f"📝 Generating terms for: {test_case['video_subject']}")
    
    response = requests.post(
        f"{CUSTOM_MODELS_URL}/terms",
        json=test_case
    )
    
    if response.status_code == 200:
        result = response.json()
        terms = result.get('video_terms', [])
        print(f"✅ Generated {len(terms)} terms:")
        for term in terms:
            print(f"   • {term}")
    else:
        print(f"❌ Failed to generate terms: {response.text}")

def test_custom_text_generation():
    """Test custom text generation"""
    print("\n✍️ Testing Custom Text Generation")
    print("=" * 40)
    
    prompts = [
        "Write a short story about a robot learning to paint",
        "Explain quantum computing in simple terms",
        "Create a recipe for chocolate chip cookies"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n📝 Prompt {i}: {prompt}")
        
        response = requests.post(
            f"{CUSTOM_MODELS_URL}/models/microsoft/DialoGPT-medium/generate",
            json={
                "prompt": prompt,
                "max_length": 200,
                "temperature": 0.7
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('generated_text', '')
            print(f"✅ Generated text ({len(generated_text)} chars):")
            print(f"   {generated_text[:150]}...")
        else:
            print(f"❌ Failed to generate text: {response.text}")

def test_performance():
    """Test model performance"""
    print("\n⚡ Testing Performance")
    print("=" * 40)
    
    prompt = "Write a short paragraph about artificial intelligence"
    
    # Test multiple generations
    times = []
    for i in range(3):
        print(f"🔄 Generation {i+1}/3...")
        start_time = time.time()
        
        response = requests.post(
            f"{CUSTOM_MODELS_URL}/models/microsoft/DialoGPT-medium/generate",
            json={
                "prompt": prompt,
                "max_length": 100,
                "temperature": 0.7
            }
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        times.append(generation_time)
        
        if response.status_code == 200:
            print(f"   ✅ Completed in {generation_time:.2f}s")
        else:
            print(f"   ❌ Failed: {response.text}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n📊 Average generation time: {avg_time:.2f}s")
        print(f"📊 Fastest: {min(times):.2f}s")
        print(f"📊 Slowest: {max(times):.2f}s")

def main():
    """Run all demo tests"""
    print("🚀 MoneyPrinterTurbo Custom Models Demo")
    print("=" * 50)
    print("Make sure MoneyPrinterTurbo is running on http://127.0.0.1:8080")
    print("=" * 50)
    
    try:
        # Test model management
        if not test_model_management():
            print("❌ Model management failed, skipping other tests")
            return
        
        # Test script generation
        test_script_generation()
        
        # Test terms generation  
        test_terms_generation()
        
        # Test custom text generation
        test_custom_text_generation()
        
        # Test performance
        test_performance()
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Tips:")
        print("   • Check /docs for full API documentation")
        print("   • Use smaller models for faster generation")
        print("   • Enable GPU for better performance")
        print("   • Models are cached after first download")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to MoneyPrinterTurbo server")
        print("   Make sure the server is running on http://127.0.0.1:8080")
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")

if __name__ == "__main__":
    main()
