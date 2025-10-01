# MoneyPrinterTurbo Custom Models - Docker Setup

This guide shows how to deploy MoneyPrinterTurbo with custom models support using Docker.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Windows
setup_docker_custom_models.bat

# Linux/Mac
./setup_docker_custom_models.sh
```

### Option 2: Manual Setup
```bash
# 1. Build the custom models image
docker-compose -f docker-compose.custom-models.yml build

# 2. Start the application
docker-compose -f docker-compose.custom-models.yml up -d

# 3. Access the WebUI
# http://localhost:8501
```

## 📋 Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM (16GB+ recommended for larger models)
- 10GB+ free disk space for models
- NVIDIA GPU with Docker support (optional, for GPU acceleration)

## 🔧 Configuration

### 1. Basic Configuration
The setup script automatically configures:
- Custom models as the default LLM provider
- Model ID: `microsoft/DialoGPT-medium`
- Device: `auto` (automatically chooses GPU if available)

### 2. Advanced Configuration
Edit `config.toml` to customize:
```toml
llm_provider = "custom"
custom_model_id = "microsoft/DialoGPT-medium"  # or your preferred model
custom_model_device = "auto"  # or "cpu", "cuda"
```

### 3. Available Models
| Model | Size | Use Case | Recommended For |
|-------|------|----------|-----------------|
| `microsoft/DialoGPT-small` | 500MB | Testing | Development |
| `microsoft/DialoGPT-medium` | 1.4GB | Production | **RECOMMENDED** |
| `microsoft/DialoGPT-large` | 3.1GB | Premium | High-quality content |
| `facebook/blenderbot-400M-distill` | 1.6GB | Educational | Conversational content |

## 🐳 Docker Commands

### Start the Application
```bash
docker-compose -f docker-compose.custom-models.yml up -d
```

### Stop the Application
```bash
docker-compose -f docker-compose.custom-models.yml down
```

### View Logs
```bash
docker-compose -f docker-compose.custom-models.yml logs -f
```

### Rebuild Image
```bash
docker-compose -f docker-compose.custom-models.yml build --no-cache
```

### Access Container Shell
```bash
docker-compose -f docker-compose.custom-models.yml exec moneypinterturbo bash
```

## 📊 Resource Management

### Memory Requirements
- **Minimum**: 4GB RAM
- **Recommended**: 8GB+ RAM
- **Large Models**: 16GB+ RAM

### Storage Requirements
- **Base Image**: ~2GB
- **Small Model**: +500MB
- **Medium Model**: +1.4GB
- **Large Model**: +3.1GB

### GPU Support
For GPU acceleration, ensure you have:
1. NVIDIA GPU with CUDA support
2. NVIDIA Docker runtime installed
3. Set `custom_model_device = "cuda"` in config

## 🔍 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'torch'"
**Solution**: The custom models dependencies aren't installed. This is normal if you're not using custom models.

**Fix**: 
- Use external APIs instead, or
- Rebuild with custom models: `docker-compose -f docker-compose.custom-models.yml build`

#### 2. "CUDA out of memory"
**Solution**: 
- Use a smaller model
- Set `custom_model_device = "cpu"`
- Increase Docker memory limits

#### 3. "Model download failed"
**Solution**:
- Check internet connection
- Ensure sufficient disk space
- Try downloading models manually

#### 4. "Custom models not available"
**Solution**:
- Check if dependencies are installed
- Rebuild the Docker image
- Check container logs

### Debug Commands

```bash
# Check container status
docker-compose -f docker-compose.custom-models.yml ps

# Check resource usage
docker stats

# Check logs
docker-compose -f docker-compose.custom-models.yml logs moneypinterturbo

# Test custom models API
curl http://localhost:8080/custom-models/models
```

## 🎯 Usage Examples

### 1. Generate Video Script
```bash
curl -X POST "http://localhost:8080/custom-models/scripts" \
  -H "Content-Type: application/json" \
  -d '{
    "video_subject": "The benefits of exercise",
    "model_id": "microsoft/DialoGPT-medium"
  }'
```

### 2. Generate Search Terms
```bash
curl -X POST "http://localhost:8080/custom-models/terms" \
  -H "Content-Type: application/json" \
  -d '{
    "video_subject": "The benefits of exercise",
    "video_script": "Exercise is important...",
    "model_id": "microsoft/DialoGPT-medium"
  }'
```

### 3. Load a Model
```bash
curl -X POST "http://localhost:8080/custom-models/models/microsoft/DialoGPT-medium/load" \
  -H "Content-Type: application/json" \
  -d '{"device": "auto"}'
```

## 🔄 Updates and Maintenance

### Update the Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.custom-models.yml down
docker-compose -f docker-compose.custom-models.yml build
docker-compose -f docker-compose.custom-models.yml up -d
```

### Clean Up
```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Full cleanup (removes everything)
docker system prune -a
```

## 📈 Performance Optimization

### 1. Memory Optimization
- Use smaller models for development
- Unload unused models
- Monitor memory usage with `docker stats`

### 2. Speed Optimization
- Use GPU acceleration when available
- Pre-load frequently used models
- Use SSD storage for models

### 3. Storage Optimization
- Use model caching
- Clean up unused models
- Use volume mounts for persistent storage

## 🛡️ Security Considerations

### 1. Network Security
- Use reverse proxy for production
- Enable HTTPS
- Restrict API access

### 2. Data Security
- Models are stored locally
- No external API calls for custom models
- Data stays within your infrastructure

### 3. Resource Security
- Set memory limits
- Monitor resource usage
- Use read-only containers where possible

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Hugging Face Models](https://huggingface.co/models)
- [Transformers Library](https://huggingface.co/docs/transformers/)
- [MoneyPrinterTurbo Documentation](https://github.com/harry0703/MoneyPrinterTurbo)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose -f docker-compose.custom-models.yml logs`
2. Check resource usage: `docker stats`
3. Verify configuration: Check `config.toml`
4. Test API endpoints: Visit `http://localhost:8080/docs`
5. Report issues on GitHub

## 🎉 Benefits Summary

✅ **No API Limits** - Generate unlimited content  
✅ **No Costs** - Completely free after setup  
✅ **Complete Privacy** - Data stays local  
✅ **Docker Ready** - Easy deployment and scaling  
✅ **GPU Support** - Automatic GPU detection  
✅ **Production Ready** - Full Docker integration  

The custom models system is now fully integrated with Docker, providing a complete local AI solution without external dependencies!
