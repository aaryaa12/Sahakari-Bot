# Free Setup Guide - Sahakari Bot

This guide explains the free, local setup for your RAG chatbot.

## Overview

Your chatbot now uses **100% free, local AI**:
- ✅ **Embeddings**: Sentence Transformers (local, free)
- ✅ **LLM**: Ollama (local, free)
- ✅ **Vector DB**: ChromaDB (already free)

**No API keys needed! No costs!**

## Installation Steps

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `sentence-transformers` - For embeddings (downloads model automatically ~80MB)
- `langchain-community` - For Ollama integration
- All other dependencies

### 2. Setup Ollama

Since you already have Ollama installed:

**Download a model:**
```bash
ollama pull llama3
```

**Start Ollama (if not running):**
```bash
ollama serve
```

Keep Ollama running in a separate terminal.

### 3. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

The backend will:
- Load sentence-transformers model (first time downloads ~80MB)
- Connect to Ollama
- Process your documents

### 4. Start Frontend

```bash
cd frontend
npm start
```

## What Changed?

### Before (OpenAI - Paid)
- ❌ Required OpenAI API key
- ❌ Cost per request
- ❌ Internet required
- ❌ API rate limits

### After (Free Local)
- ✅ No API keys needed
- ✅ Completely free
- ✅ Works offline
- ✅ No rate limits
- ✅ Full control

## Model Information

### Embeddings Model
- **Name**: `all-MiniLM-L6-v2`
- **Size**: ~80MB (downloads automatically)
- **Dimensions**: 384
- **Quality**: Excellent for RAG
- **Speed**: Very fast

### LLM Model (Ollama)
- **Default**: `llama3`
- **Size**: ~4.7GB (download once)
- **Quality**: High
- **Speed**: Fast on modern hardware

## Configuration

Edit `backend/app/core/config.py` to change models:

```python
# Change LLM model
OLLAMA_MODEL: str = "mistral"  # or "llama2", "llama3", etc.

# Change embedding model (rarely needed)
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
```

## First Run

On first run, you'll see:
1. Sentence-transformers downloading model (~80MB)
2. Backend connecting to Ollama
3. Documents being processed

This is normal and only happens once!

## Performance Tips

1. **Close other apps** - More RAM = faster responses
2. **Use SSD** - Faster model loading
3. **8GB+ RAM recommended** - For smooth operation
4. **Test before demo** - First query might be slower (model loading)

## Troubleshooting

### "Ollama connection refused"
- Make sure Ollama is running: `ollama serve`
- Check if model is downloaded: `ollama list`

### "Model not found"
- Download the model: `ollama pull llama3`
- Or change model in config to one you have

### Slow responses
- Normal for first query (model loading)
- Use smaller model if needed (llama2 instead of llama3)
- Close other applications

### Out of memory
- Use smaller model: `ollama pull llama2`
- Reduce chunk size in RAG settings
- Close other applications

## For Your Final Year Project

### Advantages to Mention:
1. **Cost-effective**: Zero operational costs
2. **Privacy**: All data stays local
3. **Offline capable**: Works without internet
4. **Customizable**: Full control over models
5. **Scalable**: Can upgrade models easily

### Demo Tips:
1. Test everything before presentation
2. Have Ollama running before demo
3. Pre-process documents beforehand
4. Show both document upload and existing files
5. Highlight the free, local architecture

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Download Ollama model: `ollama pull llama3`
3. ✅ Start Ollama: `ollama serve`
4. ✅ Start backend: `uvicorn app.main:app --reload`
5. ✅ Add your PDF/Excel files to `data/documents/`
6. ✅ Start chatting!

Enjoy your completely free RAG chatbot! 🎉
