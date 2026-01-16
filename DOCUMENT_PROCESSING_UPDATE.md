# Document Processing Update - CSV & TXT Support

## ✅ What's New

The Sahakari Bot now supports **4 file types** for RAG training data:

1. **PDF** (`.pdf`) - Regulations, compliance documents
2. **Excel** (`.xlsx`, `.xls`) - Spreadsheets, data tables  
3. **CSV** (`.csv`) - Data files, logs, structured data
4. **TXT** (`.txt`) - Plain text documents, notes

## 🚀 Key Features

### 1. **Smart File Processing**
- **Automatic Detection**: New files are automatically processed on server startup
- **Change Detection**: Modified files are automatically detected and reprocessed
- **Hash-based Tracking**: Files are tracked by content hash to detect changes
- **Duplicate Prevention**: Already processed files are skipped unless modified

### 2. **Easy File Management**
- **Add Files Anytime**: Simply drop files into `data/documents/` folder
- **Two Processing Options**:
  - **Automatic**: Restart server (processes all new/modified files)
  - **Manual**: Use reload endpoint `/api/v1/documents/reload`

### 3. **Robust File Handling**
- **Multiple Encodings**: CSV and TXT files support UTF-8, Latin-1, and other encodings
- **Large File Support**: Large CSV and TXT files are automatically chunked
- **Error Handling**: Graceful handling of corrupted or problematic files

## 📁 File Structure

```
data/documents/
├── Cooperatives-Act-2017.pdf
├── cybersecurity_policy.txt
├── compliance_data.csv
├── risk_assessment.xlsx
└── ... (any PDF, CSV, TXT, or Excel files)
```

## 🔧 How It Works

### Automatic Processing (On Startup)

1. Server starts → Scans `data/documents/` folder
2. Checks each file:
   - **New file?** → Process it
   - **Modified file?** → Remove old data, reprocess
   - **Unchanged file?** → Skip
3. All processed files are indexed in ChromaDB
4. Ready for RAG queries!

### Manual Processing

**Option 1: API Endpoint**
```bash
POST /api/v1/documents/reload?force=false
```
- `force=false`: Only process new/modified files (default)
- `force=true`: Reprocess all files

**Option 2: Web Interface**
- Use the "Reload Documents" button in the UI

## 📝 File Processing Details

### PDF Files
- Extracts text page by page
- Preserves page numbers in citations
- Handles multi-page documents

### Excel Files
- Processes all sheets
- Converts data to readable text format
- Preserves sheet names in metadata

### CSV Files
- Reads with pandas (handles encoding automatically)
- Converts to readable text format
- Splits large files into manageable chunks
- Fallback to plain text reading if pandas fails

### TXT Files
- Supports multiple encodings (UTF-8, Latin-1, etc.)
- Splits large files by paragraphs/lines
- Preserves document structure

## 🎯 Usage Examples

### Adding New Documents

1. **Copy files to folder**:
   ```bash
   cp cybersecurity_guide.pdf data/documents/
   cp training_data.csv data/documents/
   ```

2. **Process files**:
   - **Option A**: Restart backend server
   - **Option B**: Call reload endpoint

3. **Verify**:
   ```bash
   GET /api/v1/documents/status
   ```

### Updating Existing Documents

1. **Modify file** in `data/documents/`
2. **Reload** (server restart or endpoint)
3. System automatically detects change and reprocesses

## 🔍 Technical Details

### File Hash Tracking
- Each file gets an MD5 hash stored in metadata
- Hash comparison detects file changes
- Enables smart reprocessing

### Chunking Strategy
- **PDF**: By page (already chunked)
- **Excel**: By sheet
- **CSV**: By size (10,000 chars per chunk)
- **TXT**: By size (5,000 chars per chunk)
- All chunks further split by RAG service (1000 chars, 200 overlap)

### Metadata Stored
- `source`: Filename
- `page`: Page number or chunk number
- `type`: File type (pdf, excel, csv, txt)
- `file_hash`: MD5 hash for change detection
- `chunk_index`: Internal chunk index

## ⚙️ Configuration

File types are configured in `backend/app/core/config.py`:

```python
ALLOWED_EXTENSIONS: List[str] = [".pdf", ".xlsx", ".xls", ".csv", ".txt"]
EXISTING_DOCS_DIR: str = "./data/documents"
```

## 🐛 Troubleshooting

### Files Not Processing
- Check file extension is in allowed list
- Check file size < 10MB
- Check server logs for errors
- Try manual reload with `force=true`

### Encoding Issues
- CSV/TXT files: System tries multiple encodings automatically
- If issues persist, convert file to UTF-8

### Large Files
- Files are automatically chunked
- Very large files may take time to process
- Check server logs for progress

## 📊 Status Endpoint

Check document status:
```bash
GET /api/v1/documents/status
```

Returns:
```json
{
  "total_chunks": 1234,
  "ingested_files": ["file1.pdf", "file2.csv"],
  "files_count": 2,
  "has_documents": true
}
```

## ✨ Benefits

1. **Flexible Data Sources**: Support for multiple file formats
2. **Easy Updates**: Just add/modify files and reload
3. **Smart Processing**: Only processes what's needed
4. **Reliable**: Handles errors gracefully
5. **Scalable**: Works with many files

---

**Last Updated**: 2024  
**Version**: 2.0
