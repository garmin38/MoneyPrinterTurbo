#!/bin/bash

# Setup script for MoneyPrinterTurbo Custom Models with Docker
# This script sets up the environment for custom models in Docker

set -e

echo "🚀 Setting up MoneyPrinterTurbo Custom Models with Docker"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p models
mkdir -p storage
mkdir -p storage/tasks

# Set permissions
chmod 755 models
chmod 755 storage
chmod 755 storage/tasks

echo "✅ Directories created"

# Check if docker-compose.custom-models.yml exists
if [ ! -f "docker-compose.custom-models.yml" ]; then
    echo "❌ docker-compose.custom-models.yml not found"
    exit 1
fi

# Build the custom models Docker image
echo "🔨 Building Docker image with custom models support..."
docker-compose -f docker-compose.custom-models.yml build

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

# Create a simple config.toml if it doesn't exist
if [ ! -f "config.toml" ]; then
    echo "📝 Creating default config.toml..."
    cp config.example.toml config.toml
    echo "✅ Default config.toml created"
fi

# Update config.toml to use custom models
echo "⚙️  Configuring for custom models..."
if grep -q "llm_provider = \"custom\"" config.toml; then
    echo "✅ Custom models already configured"
else
    # Add custom models configuration
    cat >> config.toml << EOF

########## Custom Models (Local Hugging Face Models)
# Use local Hugging Face models without API limitations
custom_model_id = "microsoft/DialoGPT-medium"
custom_model_device = "auto"
EOF
    echo "✅ Added custom models configuration"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Start the application:"
echo "   docker-compose -f docker-compose.custom-models.yml up -d"
echo ""
echo "2. Access the WebUI:"
echo "   http://localhost:8501"
echo ""
echo "3. Access the API:"
echo "   http://localhost:8080/docs"
echo ""
echo "4. Configure custom models in the WebUI:"
echo "   - Select 'Custom' as LLM Provider"
echo "   - Set Model ID (e.g., microsoft/DialoGPT-medium)"
echo "   - Set Device (auto/cpu/cuda)"
echo ""
echo "💡 Tips:"
echo "   - Models will be downloaded automatically on first use"
echo "   - Use 'auto' device to automatically choose GPU if available"
echo "   - Check logs: docker-compose -f docker-compose.custom-models.yml logs"
echo ""
echo "🔧 Troubleshooting:"
echo "   - If models fail to load, check available memory (8GB+ recommended)"
echo "   - For GPU support, ensure NVIDIA Docker runtime is installed"
echo "   - Monitor resource usage: docker stats"
