@echo off
REM Setup script for MoneyPrinterTurbo Custom Models with Docker
REM This script sets up the environment for custom models in Docker

echo 🚀 Setting up MoneyPrinterTurbo Custom Models with Docker
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist models mkdir models
if not exist storage mkdir storage
if not exist storage\tasks mkdir storage\tasks

echo ✅ Directories created

REM Check if docker-compose.custom-models.yml exists
if not exist "docker-compose.custom-models.yml" (
    echo ❌ docker-compose.custom-models.yml not found
    exit /b 1
)

REM Build the custom models Docker image
echo 🔨 Building Docker image with custom models support...
docker-compose -f docker-compose.custom-models.yml build

if %errorlevel% neq 0 (
    echo ❌ Failed to build Docker image
    exit /b 1
)

echo ✅ Docker image built successfully

REM Create a simple config.toml if it doesn't exist
if not exist "config.toml" (
    echo 📝 Creating default config.toml...
    copy config.example.toml config.toml
    echo ✅ Default config.toml created
)

REM Update config.toml to use custom models
echo ⚙️  Configuring for custom models...
findstr /C:"llm_provider = \"custom\"" config.toml >nul
if %errorlevel% neq 0 (
    REM Add custom models configuration
    echo. >> config.toml
    echo ########## Custom Models (Local Hugging Face Models) >> config.toml
    echo # Use local Hugging Face models without API limitations >> config.toml
    echo custom_model_id = "microsoft/DialoGPT-medium" >> config.toml
    echo custom_model_device = "auto" >> config.toml
    echo ✅ Added custom models configuration
) else (
    echo ✅ Custom models already configured
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Start the application:
echo    docker-compose -f docker-compose.custom-models.yml up -d
echo.
echo 2. Download models (optional):
echo    docker-compose -f docker-compose.custom-models.yml exec moneypinterturbo python setup_models_docker.py --recommended
echo.
echo 3. Access the WebUI:
echo    http://localhost:8501
echo.
echo 4. Access the API:
echo    http://localhost:8080/docs
echo.
echo 5. Configure custom models in the WebUI:
echo    - Select 'Custom' as LLM Provider
echo    - Set Model ID (e.g., microsoft/DialoGPT-medium)
echo    - Set Device (auto/cpu/cuda)
echo.
echo 💡 Tips:
echo    - Models can be downloaded automatically on first use
echo    - Or download them now with the command above
echo    - Use 'auto' device to automatically choose GPU if available
echo    - Check logs: docker-compose -f docker-compose.custom-models.yml logs
echo.
echo 🔧 Troubleshooting:
echo    - If models fail to load, check available memory (8GB+ recommended)
echo    - For GPU support, ensure NVIDIA Docker runtime is installed
echo    - Monitor resource usage: docker stats

pause
