# Documents Folder

Place your cybersecurity compliance documents, regulations, and training materials in this folder.

## How it works

1. **Automatic Loading**: When the backend server starts, it automatically scans this folder and ingests all supported files into the vector database.

2. **Smart Processing**: 
   - New files are automatically processed
   - Modified files are detected and reprocessed
   - Already processed files are skipped (unless modified)

3. **Supported Formats**:
   - PDF files (`.pdf`) - Regulations, compliance documents
   - Excel files (`.xlsx`, `.xls`) - Spreadsheets, data tables
   - CSV files (`.csv`) - Data files, logs
   - Text files (`.txt`) - Plain text documents, notes

## Adding Documents

Simply copy your files into this folder:

```
data/documents/
├── Cooperatives-Act-2017.pdf
├── cybersecurity_policy.txt
├── compliance_data.csv
└── risk_assessment.xlsx
```

**Two ways to process files:**

1. **Automatic (Recommended)**: Restart the backend server - all new/modified files will be processed automatically
2. **Manual**: Use the "Reload Documents" button in the web interface or call the `/api/v1/documents/reload` endpoint

## File Size Limit

Maximum file size: 10MB per file

## Notes

- Files are processed on server startup automatically
- If you add or modify files, you can either:
  - Restart the server (automatic processing)
  - Use the reload endpoint (manual processing)
- Modified files are automatically detected and reprocessed
- Files are indexed by filename and content hash
- The chatbot will answer questions based on the content of these documents
- All file types are processed and made searchable through the RAG system