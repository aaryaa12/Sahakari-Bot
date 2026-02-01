# Windows Setup (Recommended)

This setup avoids version issues by standardizing Python.

## Requirements
- Windows 10/11
- Python 3.11 (recommended) or 3.10
- Node.js 18+
- Ollama

## One-Time Setup (PowerShell)
Run from the project root:

```powershell
.\setup.ps1
```

## Manual Setup (if you prefer)

### 1) Backend (Python)
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### 2) Ollama
```powershell
ollama pull llama3
ollama serve
```

### 3) Backend server
```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

### 4) Frontend
```powershell
cd frontend
npm install
npm start
```

## Notes
- Always use the project virtual environment (`backend\.venv`) when running backend.
- If a device has multiple Python versions, this avoids mismatches.
