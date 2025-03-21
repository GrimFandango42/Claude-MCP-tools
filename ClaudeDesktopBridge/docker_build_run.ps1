# PowerShell script to build and run the Claude Desktop Bridge Docker container

# Check if .env file exists
if (-not (Test-Path -Path ".env")) {
    Write-Host "Error: .env file not found. Please create it from .env.example" -ForegroundColor Red
    Write-Host "Copy .env.example to .env and fill in your API keys" -ForegroundColor Yellow
    exit 1
}

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Cyan
docker build -t claude-desktop-bridge .

# Check if build was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker build failed" -ForegroundColor Red
    exit 1
}

# Run the Docker container
Write-Host "Running Docker container..." -ForegroundColor Cyan
docker run -d --name claude-desktop-bridge \
    -p 8000:8000 \
    -v "${PWD}/screenshots:/app/screenshots" \
    -v "${PWD}/.env:/app/.env" \
    --restart unless-stopped \
    claude-desktop-bridge

# Check if container started successfully
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to start Docker container" -ForegroundColor Red
    exit 1
}

# Show container status
Write-Host "Container started successfully!" -ForegroundColor Green
Write-Host "API is available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Streamlit UI can be started with: python -m streamlit run app/ui/streamlit_app.py" -ForegroundColor Cyan

# Show logs
Write-Host "Showing container logs (Ctrl+C to exit)..." -ForegroundColor Yellow
docker logs -f claude-desktop-bridge
