# MoneyPrinterTurbo Custom Models

This feature allows you to use local Hugging Face models instead of external APIs, eliminating rate limits and costs while providing full control over your AI models.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements-custom-models.txt
```

### 2. Setup Custom Models
```bash
python setup_custom_models.py
```

### 3. Configure MoneyPrinterTurbo
Edit your `config.toml`:
```toml
llm_provider = "custom"
custom_model_id = "microsoft/DialoGPT-medium"
custom_model_device = "auto"  # or "cpu", "cuda"
```

### 4. Restart the Application
```bash
python main.py
```

## 📋 Available Models

| Model | Size | Parameters | Use Case | Description |
|-------|------|------------|----------|-------------|
| `microsoft/DialoGPT-small` | ~500MB | 117M | Conversational | Lightweight chat model |
| `microsoft/DialoGPT-medium` | ~1.4GB | 345M | Conversational | Balanced performance |
| `microsoft/DialoGPT-large` | ~3.1GB | 774M | Conversational | High-quality responses |
| `facebook/blenderbot-400M-distill` | ~1.6GB | 400M | Conversational | Facebook's chat model |
| `EleutherAI/gpt-neo-125M` | ~500MB | 125M | Text Generation | Small GPT-style model |
| `EleutherAI/gpt-neo-1.3B` | ~5.2GB | 1.3B | Text Generation | Medium GPT-style model |

## 🔧 API Endpoints

### List Available Models
```http
GET /custom-models/models
```

### Load a Model
```http
POST /custom-models/models/{model_id}/load
Content-Type: application/json

{
  "device": "auto"
}
```

### Generate Video Script
```http
POST /custom-models/scripts
Content-Type: application/json

{
  "video_subject": "The benefits of exercise",
  "language": "en",
  "paragraph_number": 1,
  "model_id": "microsoft/DialoGPT-medium"
}
```

### Generate Search Terms
```http
POST /custom-models/terms
Content-Type: application/json

{
  "video_subject": "The benefits of exercise",
  "video_script": "Exercise is important for health...",
  "amount": 5,
  "model_id": "microsoft/DialoGPT-medium"
}
```

### Generate Custom Text
```http
POST /custom-models/models/{model_id}/generate
Content-Type: application/json

{
  "prompt": "Write a short story about a robot",
  "max_length": 500,
  "temperature": 0.7
}
```

## ⚙️ Configuration

### Model Settings
Edit `models/model_configs.json` to customize model parameters:

```json
{
  "microsoft/DialoGPT-medium": {
    "name": "DialoGPT Medium",
    "description": "Medium conversational AI model",
    "max_length": 1000,
    "temperature": 0.7,
    "do_sample": true,
    "pad_token_id": null
  }
}
```

### Device Configuration
- `"auto"`: Automatically choose GPU if available, otherwise CPU
- `"cpu"`: Force CPU usage (slower but works on any system)
- `"cuda"`: Force GPU usage (faster but requires CUDA-compatible GPU)

## 🎯 Use Cases

### 1. No API Limits
- Generate unlimited scripts and terms
- No rate limiting or usage quotas
- Complete privacy - data stays local

### 2. Cost Savings
- No per-token charges
- No monthly API subscriptions
- One-time setup cost

### 3. Customization
- Fine-tune models for your specific needs
- Adjust parameters for different use cases
- Add your own custom models

### 4. Offline Operation
- Works without internet connection
- No dependency on external services
- Perfect for air-gapped environments

## 🔧 Advanced Usage

### Adding Custom Models
1. Add your model to `models/model_configs.json`:
```json
{
  "your-org/your-model": {
    "name": "Your Custom Model",
    "description": "Your model description",
    "max_length": 1000,
    "temperature": 0.7,
    "do_sample": true
  }
}
```

2. Load the model via API:
```http
POST /custom-models/models/your-org/your-model/load
```

### Model Management
- **Load**: Models are loaded into memory when first used
- **Unload**: Use the unload endpoint to free memory
- **Cache**: Models are cached locally after first download
- **Update**: Re-run setup script to update model configurations

### Performance Tips
1. **Start Small**: Begin with DialoGPT-small for testing
2. **Use GPU**: Enable CUDA for 3-5x faster inference
3. **Memory Management**: Unload unused models to free RAM
4. **Batch Processing**: Process multiple requests together

## 🐛 Troubleshooting

### Common Issues

**"Model not found"**
- Ensure the model ID is correct
- Check that the model is in `model_configs.json`
- Verify internet connection for first-time downloads

**"CUDA out of memory"**
- Use a smaller model
- Set `device: "cpu"` in the load request
- Close other applications to free GPU memory

**"Slow performance"**
- Enable GPU acceleration
- Use smaller models for faster inference
- Consider model quantization for memory efficiency

### System Requirements

**Minimum:**
- 4GB RAM
- 10GB free disk space
- Python 3.8+

**Recommended:**
- 8GB+ RAM
- 20GB+ free disk space
- NVIDIA GPU with 4GB+ VRAM
- Python 3.9+

## 📚 Model Information

### DialoGPT Models
- **Best for**: Conversational AI, chat applications
- **Strengths**: Natural dialogue, context awareness
- **Use cases**: Video scripts, interactive content

### BlenderBot
- **Best for**: Multi-turn conversations
- **Strengths**: Knowledge retention, empathy
- **Use cases**: Educational content, Q&A videos

### GPT-Neo Models
- **Best for**: General text generation
- **Strengths**: Creative writing, diverse topics
- **Use cases**: Creative scripts, varied content

## 🔄 Migration from External APIs

1. **Backup your config**: Save your current `config.toml`
2. **Install dependencies**: Run the setup script
3. **Test with small model**: Start with DialoGPT-small
4. **Gradually scale up**: Move to larger models as needed
5. **Update workflows**: Modify any custom scripts to use new endpoints

## 📞 Support

- **Issues**: Report problems on GitHub Issues
- **Documentation**: Check `/docs` endpoint for full API docs
- **Community**: Join discussions in the project repository

## 🎉 Benefits Summary

✅ **No API Limits** - Generate unlimited content  
✅ **Cost Effective** - No per-token charges  
✅ **Privacy First** - Data stays on your machine  
✅ **Offline Ready** - Works without internet  
✅ **Fully Customizable** - Add your own models  
✅ **Easy Integration** - Drop-in replacement for external APIs  

Start with a small model and scale up as needed. The custom models feature gives you complete control over your AI-powered video generation workflow!
