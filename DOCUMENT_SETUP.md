# Document Setup Guide

This guide explains how to set up your chatbot to work with existing PDF and Excel files.

## Overview

The Sahakari Bot chatbot can answer questions based on:
1. **Existing documents** - PDF/Excel files you place in a folder (automatically loaded on startup)
2. **Uploaded documents** - Files uploaded through the web interface

## Setting Up Existing Documents

### Step 1: Place Your Files

Place your PDF and Excel files in the following folder:
```
data/documents/
```

**Supported file formats:**
- PDF files (`.pdf`)
- Excel files (`.xlsx`, `.xls`)

**Example:**
```
data/documents/
├── cybersecurity_regulations.pdf
├── compliance_guide.xlsx
├── risk_assessment.xls
└── insider_threat_policy.pdf
```

### Step 2: Start the Backend Server

When you start the backend server, it will automatically:
1. Scan the `data/documents/` folder
2. Process any new PDF/Excel files found
3. Extract text and create embeddings
4. Store them in the vector database (ChromaDB)

**You'll see logs like:**
```
INFO - Found 3 document(s) in ./data/documents
INFO - Processing 3 new document(s)...
INFO - Processing: cybersecurity_regulations.pdf
INFO - ✓ Successfully ingested cybersecurity_regulations.pdf (45 chunks)
```

### Step 3: Ask Questions

Once the documents are processed, you can ask questions in the chat interface, and the bot will answer based on the content of your documents.

## Uploading Documents via Web Interface

You can also upload documents through the web interface:

1. Log in to the application
2. Click the "Upload" button in the header
3. Select a PDF or Excel file
4. The file will be processed and added to the knowledge base

## How It Works

### Automatic Processing
- Files are processed on **server startup**
- Only **new files** are processed (duplicates are skipped)
- Files are identified by filename

### Document Processing Flow
1. **Text Extraction**: 
   - PDFs: Extracted page by page using pdfplumber
   - Excel: Each sheet is converted to text using pandas
2. **Chunking**: Text is split into smaller chunks (1000 characters with 200 overlap)
3. **Embedding**: Each chunk is converted to a vector embedding using OpenAI
4. **Storage**: Embeddings are stored in ChromaDB for fast similarity search

### Query Processing
When you ask a question:
1. Your question is converted to an embedding
2. The system searches for similar chunks in the database
3. Relevant context is retrieved
4. GPT-3.5 generates an answer based on the context
5. Citations show which document and page the answer came from

## Manual Reload

If you add new files to `data/documents/` after the server has started, you can:

**Option 1:** Restart the server (recommended)

**Option 2:** Use the API endpoint (if you have access):
```
POST /api/v1/documents/reload
```

## Troubleshooting

### Files Not Being Processed

1. **Check file location**: Ensure files are in `data/documents/` folder
2. **Check file format**: Only `.pdf`, `.xlsx`, and `.xls` files are supported
3. **Check file size**: Maximum 10MB per file
4. **Check server logs**: Look for error messages during startup

### Duplicate Files

- Files are identified by filename
- If a file with the same name already exists in the database, it won't be re-processed
- To re-process a file, delete it from ChromaDB or rename the file

### Empty or Corrupted Files

- The system will skip files that can't be processed
- Check server logs for specific error messages
- Ensure PDFs are not password-protected or corrupted
- Ensure Excel files are in a readable format

## File Organization Tips

1. **Use descriptive filenames**: The filename appears in citations
2. **Organize by topic**: You can create subfolders (though the system currently scans only the root)
3. **Keep files updated**: Replace old files with updated versions (remember to restart the server)

## Next Steps

1. Add your PDF/Excel files to `data/documents/`
2. Start the backend server
3. Check the logs to confirm files were processed
4. Start asking questions in the chat interface!
