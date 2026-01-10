# Quick Start Guide - Free RAG Chatbot

## ✅ What's Changed

Your chatbot is now **100% FREE** using:

- **Sentence Transformers** (local embeddings) - No setup needed, downloads automatically
- **Ollama** (local LLM) - You already have this!
- **ChromaDB** (vector database) - Already free

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

_Note: This will download sentence-transformers model (~80MB) automatically on first use_

### Step 2: Download Ollama Model

```bash
ollama pull llama3
```

_This downloads the LLM model (~4.7GB, one-time download)_

### Step 3: Start Everything

**Terminal 1 - Start Ollama:**

```bash
ollama serve
```

**Terminal 2 - Start Backend:**

```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 3 - Start Frontend:**

```bash
cd frontend
npm start
```

## 📁 Add Your Documents

Place your PDF/Excel files in:

```
data/documents/
```

The backend will automatically process them on startup!

## 🎯 Test It

1. Open http://localhost:3000
2. Register/Login
3. Ask a question about your documents!

## ⚠️ Troubleshooting

### "Ollama connection refused"

- Make sure `ollama serve` is running
- Check: `curl http://localhost:11434/api/tags`

### "Model not found"

- Download model: `ollama pull llama3`
- Or change model in `backend/app/core/config.py`

### Slow first response

- Normal! Model loads on first use
- Subsequent queries will be faster

## 📚 More Info

- **Ollama Setup**: See `backend/OLLAMA_SETUP.md`
- **Free Setup Guide**: See `FREE_SETUP.md`
- **Document Setup**: See `DOCUMENT_SETUP.md`

## 🎓 For Your Project

**Key Points to Mention:**

- ✅ Zero cost (completely free)
- ✅ Privacy (all data local)
- ✅ Offline capable
- ✅ Modern RAG architecture
- ✅ Professional implementation

**Demo Tips:**

- Test before presentation
- Have Ollama running
- Pre-process documents
- Show both upload and existing files features

---

**That's it! You're ready to go! 🚀**
