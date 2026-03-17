# Stop any existing Python processes
Write-Host "🛑 Stopping existing Python processes..."
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait
Start-Sleep -Seconds 2

# Navigate to project directory
Set-Location "c:\Users\user1\Documents\תכנות\AI\cli_agent"

# Run the app
Write-Host "🚀 Starting Gradio app..."
Write-Host "📍 Server will be at: http://127.0.0.1:7860"
Write-Host ""

uv run main.py
