# Documents Folder

Place your existing PDF and Excel files in this folder.

## How it works

1. **Automatic Loading**: When the backend server starts, it automatically scans this folder and ingests all PDF (.pdf) and Excel (.xlsx, .xls) files into the vector database.

2. **Duplicate Prevention**: Files that have already been processed will be skipped automatically.

3. **Supported Formats**:
   - PDF files (`.pdf`)
   - Excel files (`.xlsx`, `.xls`)

## Adding Documents

Simply copy your PDF or Excel files into this folder:

```
data/documents/
├── regulation.pdf
├── compliance_guide.xlsx
└── risk_assessment.xls
```

After placing files here, restart the backend server. The files will be automatically processed and made available to the chatbot.

## File Size Limit

Maximum file size: 10MB per file

## Notes

- Files are processed on server startup
- If you add new files, restart the server to process them
- Files are indexed by filename, so duplicate filenames will be treated as the same document
- The chatbot will answer questions based on the content of these documents
