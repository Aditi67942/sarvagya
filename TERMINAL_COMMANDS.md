# TERMINAL COMMANDS - Phase 1 Setup & Execution Guide
## Copy-Paste Friendly Commands for Windows PowerShell

---

## 🎯 QUICK START (2 minutes)

```powershell
# Terminal 1: Backend Setup
cd C:\Users\51429\OneDrive\Desktop\sarvagya\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 9000

# Terminal 2: Frontend Setup (while backend is running)
cd C:\Users\51429\OneDrive\Desktop\sarvagya\frontend
npm install
npm run dev

# Terminal 3: Test (while both are running)
curl -X GET "http://localhost:9000/api/v1/health"
```

---

## 📋 DETAILED SETUP INSTRUCTIONS

### **STEP 1: Initial Backend Setup**

Run these commands **ONLY ONCE** to set up the Python environment:

```powershell
# Navigate to backend directory
cd "C:\Users\51429\OneDrive\Desktop\sarvagya\backend"

# Create Python virtual environment (venv)
python -m venv venv

# Activate virtual environment
# (Add ". \" to PATH so Python packages install locally)
.\venv\Scripts\Activate.ps1

# You should see: (venv) PS C:\...

# Install all Python dependencies from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list | findstr fastapi
```

**Expected Output:**
```
(venv) PS C:\Users\51429\OneDrive\Desktop\sarvagya\backend>
fastapi                    0.135.1
uvicorn                    0.41.0
pydantic-settings          2.13.1
```

---

### **STEP 2: Configure Environment Secrets**

```powershell
# Copy template to actual config file
cp .env.example .env

# Edit .env with your actual API keys
# You can use VS Code or Notepad:
code .env
# (or: notepad .env)

# Required fields to fill:
# - SARVAM_API_KEY=sk_your_key_here
# - GEMINI_API_KEY=your_key_here
# - GOOGLE_VISION_API_KEY=your_key_here
```

**For Google Vision (Optional but Recommended):**

```powershell
# If you want to use Google Vision, place service account JSON here:
# File: backend/credentials/google_service_account.json
# Get from: https://cloud.google.com/docs/authentication/getting-started

# Verify it exists:
ls credentials/
# Should show: google_service_account.json
```

---

### **STEP 3: Initial Frontend Setup**

Run these commands **ONLY ONCE** to set up Node.js environment:

```powershell
# Navigate to frontend directory
cd "C:\Users\51429\OneDrive\Desktop\sarvagya\frontend"

# Install Node dependencies
npm install

# Verify installation
npm list react zustand
```

**Expected Output:**
```
frontend@0.0.0 C:\Users\51429\OneDrive\Desktop\sarvagya\frontend
├── react@19.2.4
├── react-dom@19.2.4
└── zustand@5.0.11
```

---

## 🚀 STARTING DEVELOPMENT (Run Every Day)

### **Backend Server**

**Terminal Window 1:**
```powershell
cd "C:\Users\51429\OneDrive\Desktop\sarvagya\backend"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start FastAPI server with hot reload
uvicorn main:app --reload --port 9000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:9000
INFO:     Application startup complete
INFO:     ✅  [Sarvagya] Starting in 'development' mode
INFO:     📁  Upload directory: ./uploads
```

**To Stop:** Press `Ctrl+C`

---

### **Frontend Dev Server**

**Terminal Window 2** (keep backend running in Terminal 1):
```powershell
cd "C:\Users\51429\OneDrive\Desktop\sarvagya\frontend"

# Start Vite development server
npm run dev
```

**Expected Output:**
```
VITE v5.x.x

➜  Local:   http://localhost:5173/
➜  press h + enter to show help
```

**To Stop:** Press `q` then `Enter`

---

## 🧪 TESTING THE PIPELINE

### **Test 1: Backend Health Check**

```powershell
# Terminal 3 (new PowerShell window)
curl -X GET "http://localhost:9000/api/v1/health"
```

**Expected Response:**
```json
{
  "status": "ok",
  "app": "Sarvagya",
  "env": "development",
  "version": "0.1.0"
}
```

---

### **Test 2: Pipeline Status**

```powershell
curl -X GET "http://localhost:9000/api/v1/pipeline/status"
```

**Expected Response:**
```json
{
  "ocr_providers": ["sarvam", "google_vision", "gemini"],
  "azure": "not configured yet",
  "status": "ready"
}
```

---

### **Test 3: Upload Image to Pipeline**

```powershell
# First, save this Python script as test_pipeline.py
# in the backend directory

# ===== test_pipeline.py =====
import httpx
import base64
from pathlib import Path

# Read your test image
image_path = Path("test_image.jpg")  # Place any JPG image here
if not image_path.exists():
    print("ERROR: Place test_image.jpg in backend directory")
    exit(1)

image_base64 = base64.b64encode(image_path.read_bytes()).decode()

# Post to pipeline
async def test():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9000/api/v1/pipeline",
            files={"file": image_path.open("rb")}
        )
        print(response.status_code)
        print(response.json())

import asyncio
asyncio.run(test())
# ===== end test_pipeline.py =====

# Run it:
python test_pipeline.py
```

**Or use curl (simpler):**

```powershell
# Place test_image.jpg in backend directory, then:
curl -X POST "http://localhost:9000/api/v1/pipeline" `
  -Form @{file=@"test_image.jpg"}
```

**Expected Response:**
```json
{
  "ocr": {
    "final_text": "extracted text from image...",
    "winning_provider": "sarvam",
    "all_results": [...]
  },
  "translation": {...},
  "braille": {...},
  "tts": {...}
}
```

---

### **Test 4: Open Frontend in Browser**

```powershell
# Simply open in any browser:
# http://localhost:5173

# Or from PowerShell:
Start-Process "http://localhost:5173"
```

---

## 🔧 TROUBLESHOOTING COMMANDS

### **Port Already in Use**

```powershell
# Find process using port 9000
netstat -ano | findstr :9000

# Kill it (replace PID with actual process ID)
taskkill /PID 12345 /F

# For port 5173 (frontend):
netstat -ano | findstr :5173
taskkill /PID 54321 /F
```

---

### **Virtual Environment Issues**

```powershell
# Verify venv is activated
# (should show "(venv)" in PowerShell prompt)

# If not activated, manually activate again:
cd "backend"
.\venv\Scripts\Activate.ps1

# Check Python is from venv:
which python
# Should show: C:\...sarvagya\backend\venv\Scripts\python.exe

# List all installed packages:
pip list

# Upgrade pip (if needed):
python -m pip install --upgrade pip
```

---

### **Dependencies Installation Issues**

```powershell
# Clear pip cache and reinstall:
pip cache purge
pip install --no-cache-dir -r requirements.txt

# Or create fresh venv:
deactivate          # Exit current venv
rm -r venv          # Delete old venv
python -m venv venv # Create new
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### **Frontend Dependencies Issues**

```powershell
# Clear npm cache and reinstall:
npm cache clean --force
rm -r node_modules
npm install

# Check for version conflicts:
npm audit

# Update all packages to latest:
npm update
```

---

### **API Connection Issues**

```powershell
# Test backend is actually running on http://localhost:9000:
curl http://localhost:9000

# Check CORS is configured correctly:
# Look for Access-Control-Allow-Origin in response headers:
curl -i http://localhost:9000/api/v1/health

# Expected headers:
# Access-Control-Allow-Origin: http://localhost:5173
# Access-Control-Allow-Methods: *
```

---

## 📊 ENVIRONMENT VARIABLE SETUP

### **For Backend:**

```powershell
# From backend directory
code .env  # or: notepad .env

# Paste and edit:
APP_NAME=Sarvagya
APP_ENV=development
DEBUG=true

SARVAM_API_KEY=sk_PASTE_YOUR_KEY_HERE
SARVAM_BASE_URL=https://api.sarvam.ai

GOOGLE_APPLICATION_CREDENTIALS=./credentials/google_service_account.json
GOOGLE_VISION_API_KEY=PASTE_YOUR_KEY_HERE

GEMINI_API_KEY=PASTE_YOUR_KEY_HERE

MAX_UPLOAD_SIZE_MB=10
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf,tiff
UPLOAD_DIR=./uploads

ALLOWED_ORIGINS=http://localhost:5173
```

### **For Frontend (Optional):**

```powershell
# From frontend directory
code .env  # or: notepad .env

# Paste:
VITE_API_BASE_URL=http://localhost:9000
```

---

## 📈 DEVELOPMENT WORKFLOW

**Each Development Session:**

```powershell
# Terminal 1: Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 9000

# Terminal 2: Frontend (in new PowerShell window)
cd frontend
npm run dev

# Terminal 3: Testing/git (in new PowerShell window)
cd .
# Use this terminal for git commands, manual tests, etc.
```

**Git Workflow:**

```powershell
# Check status
git status

# Add changes
git add --all

# Commit with message
git commit -m "Fix: braille type mismatch"

# Push (if you have Git configured)
git push origin main
```

---

## 🧹 CLEANUP / RESET

### **To Fully Reset Backend:**

```powershell
cd "C:\Users\51429\OneDrive\Desktop\sarvagya\backend"

# Remove venv
deactivate
rm -r venv

# Remove Python cache
rm -r __pycache__
ls -r -Include "__pycache__" | rm

# Remove uploaded files (optional)
rm uploads/*

# Reinstall everything:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### **To Fully Reset Frontend:**

```powershell
cd "C:\Users\51429\OneDrive\Desktop\sarvagya\frontend"

# Remove node_modules
rm -r node_modules

# Remove npm cache
npm cache clean --force

# Reinstall:
npm install
```

---

## 📝 ONE-LINER USEFUL COMMANDS

```powershell
# Check Python version
python --version

# Check pip packages
pip list | grep -E "fastapi|pydantic|httpx"

# Check Node version
node --version

# View backend logs (last 20 lines)
tail -n 20 backend.log

# Start everything at once (from root):
Start-Job { cd backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload --port 9000 } -Name backend; Start-Job { cd frontend; npm run dev } -Name frontend

# Stop all jobs:
Get-Job | Stop-Job
```

---

## 🎓 LEARNING RESOURCES

```powershell
# Test FastAPI documentation:
# Visit: http://localhost:9000/docs
# Visit: http://localhost:9000/redoc

# Check actual OpenAPI schema:
curl http://localhost:9000/openapi.json | python -m json.tool
```

---

## ✅ FINAL VERIFICATION CHECKLIST

Before claiming "Phase 1 complete," verify:

```powershell
# ✓ Backend starts without errors
uvicorn main:app --reload --port 9000

# ✓ Health endpoint responds
curl http://localhost:9000/api/v1/health

# ✓ Frontend starts without errors
npm run dev

# ✓ Frontend loads in browser
# http://localhost:5173

# ✓ No TypeErrors or ValidationErrors in console
# (check browser DevTools: F12)

# ✓ .env file is created and .env is in .gitignore
git status
# Should NOT show: backend/.env

# ✓ All services initialized
# Check FastAPI logs for startup messages:
# ✅ [Sarvagya] Starting in 'development' mode
# 📁 Upload directory: ./uploads
```

---

**Status:** ✅ Terminal Commands Ready  
**Phase:** 1 Complete  
**Next:** Phase 2 Setup (Begin with Sarvam SDK integration)
