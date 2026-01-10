# Ollama Setup Guide

This guide will help you set up Ollama for the Sahakari Bot project.

## Prerequisites

✅ You mentioned you already have Ollama installed - great!

## Step 1: Verify Ollama is Running

Open a terminal and run:
```bash
ollama --version
```

If Ollama is not running, start it:
```bash
ollama serve
```

Keep this terminal open while running the backend.

## Step 2: Download Required Model

You need to download at least one LLM model. Recommended models:

### Option 1: Llama 3 (Recommended - Best Quality)
```bash
ollama pull llama3
```
**Size:** ~4.7GB  
**Best for:** High-quality responses, good for RAG

### Option 2: Mistral (Alternative - Good Balance)
```bash
ollama pull mistral
```
**Size:** ~4.1GB  
**Best for:** Good quality, slightly faster

### Option 3: Llama 2 (Smaller - Faster)
```bash
ollama pull llama2
```
**Size:** ~3.8GB  
**Best for:** Lower RAM usage, faster responses

## Step 3: Verify Model is Available

List all downloaded models:
```bash
ollama list
```

You should see your model in the list.

## Step 4: Test the Model

Test if the model works:
```bash
ollama run llama3
```

Type a test message and press Enter. If it responds, you're good to go!

## Step 5: Configure Backend (Optional)

The backend is configured to use `llama3` by default. If you want to use a different model:

1. Edit `backend/app/core/config.py`
2. Change `OLLAMA_MODEL: str = "llama3"` to your preferred model (e.g., `"mistral"`)

Or set it via environment variable:
```bash
export OLLAMA_MODEL=mistral
```

## Troubleshooting

### Ollama Not Found
- Make sure Ollama is installed: https://ollama.ai/download
- Add Ollama to your PATH

### Model Not Found Error
- Make sure you've downloaded the model: `ollama pull llama3`
- Check model name matches in config

### Connection Refused
- Make sure Ollama is running: `ollama serve`
- Check if it's running on port 11434: `curl http://localhost:11434/api/tags`

### Out of Memory
- Use a smaller model (llama2 instead of llama3)
- Close other applications
- Reduce chunk size in RAG settings

## Recommended Setup for Final Year Project

For your project demo, I recommend:
1. **Use Llama 3** - Best quality for impressive demo
2. **Have 8GB+ RAM available** - Close other apps during demo
3. **Test before presentation** - Make sure everything works

## Quick Start Commands

```bash
# Start Ollama (in one terminal)
ollama serve

# Download model (in another terminal)
ollama pull llama3

# Verify it works
ollama run llama3 "Hello, can you help me?"
```

That's it! Your backend will automatically use Ollama when you start it.
