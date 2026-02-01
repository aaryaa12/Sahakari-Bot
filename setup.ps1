param(
  [string]$PythonVersion = "3.11"
)

$ErrorActionPreference = "Stop"

Write-Host "== Sahakari Bot setup (Windows) =="
Write-Host "Python: $PythonVersion"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
  Write-Host "ERROR: Python launcher 'py' not found. Install Python first." -ForegroundColor Red
  exit 1
}

Write-Host "Creating virtual environment..."
Push-Location "backend"
py -$PythonVersion -m venv .venv

Write-Host "Activating virtual environment..."
& ".\.venv\Scripts\activate"

Write-Host "Installing backend dependencies..."
python -m pip install -r requirements.txt
Pop-Location

Write-Host ""
Write-Host "Backend setup complete."
Write-Host "Next steps:"
Write-Host "1) Start Ollama:  ollama serve"
Write-Host "2) Start backend: cd backend; .\.venv\Scripts\activate; uvicorn app.main:app --reload"
Write-Host "3) Start frontend: cd frontend; npm install; npm start"
