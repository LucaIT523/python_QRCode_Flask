# 

<div align="center">
   <h1>QR information recognition and classification of PDF files integrated with Flask API</h1>
</div>

### Testing Method:

Please see readme.docx and readme_flask.docx file



### Inputed QR image and Result :



<div align="center">
   <img src=https://github.com/LucaIT523/python_QRCode_Flask/blob/main/images/1.png>
</div>



<div align="center">
   <img src=https://github.com/LucaIT523/python_QRCode_Flask/blob/main/images/2.png>
</div>





### 1. System Architecture

The solution comprises two main components:

1. **PDF Processing Engine** (`pdf_qrcode_flask.py`)
   - QR Code-based document segmentation
   - OCR-based page number recognition
   - Multi-page PDF reconstruction
2. **Web Service Layer** (Flask server)
   - REST API endpoints for file upload/status checking
   - Asynchronous task handling
   - Unique session management

### 2. Core Workflow

```
[Client] → Upload PDF → [Flask Server] → 
→ Background Processing → 
→ [QR Detection] → [OCR Analysis] → [PDF Segmentation] → 
→ [Client Polling] → Return JSON Results
```

### 3. Key Technical Components

#### 3.1 PDF Processing Engine

**A. QR Code Extraction**

```
def GetQRInfo(image_path):
    return decode(Image.open(image_path))[0].data.decode('ascii')
```

- Uses `pyzbar` for QR decoding
- Scans top/bottom 20% of pages (header/footer regions)
- Implements image upscaling (200%) for better recognition

**B. Page Number OCR**

```
def GetPageInfo():
    # OCR error correction through character substitution
    text.replace("I","1").replace("$","8")...
    # Pattern matching for "Page X of Y" format
```

- Handles 15+ common OCR misinterpretations
- Fallback to (0,0) for failed extractions

**C. Document Segmentation**

```
def create_sub_pdf():
    im1.save(qr_info, save_all=True, append_images=image_list)
```

- Creates sub-PDFs using original image sequence
- Naming format: `[start_page]~[end_page]_[QR_content].pdf`

#### 3.2 Flask Web Service

**A. Asynchronous Processing**

```
thread = threading.Thread(target=execute_python_file...)
thread.start()
```

- Background thread execution for PDF processing
- UUID-based session management
- State tracking through progress files (10-100%)

**B. API Endpoints**

```
@app.route('/api/qr_upload', methods=['POST'])  # File upload
@app.route('/api/qr_state', methods=['POST'])   # Progress check
```

- JSON-based communication protocol
- Error handling for file operations

**C. Security Features**

- UUID-based temporary directories
- File path sanitization
- Process isolation through subdirectories

### 4. Operational Characteristics

**Performance Considerations**

- Multi-threaded architecture prevents server blocking
- Temporary file cleanup post-processing
- Platform-independent execution (Windows/Linux)

**State Management**

```
work_dir/
├── [UUID]/
│   ├── state    # Progress percentage
│   └── result   # Final JSON output
└── temp/        # Transient conversion files
```

### 5. Development Considerations

**Dependency Management**

- Requires Tesseract OCR (Windows path hardcoded)
- Relies on `pdf2image` for PDF conversion
- Uses OpenCV for image processing

**Error Handling**

- Try-catch blocks for OCR failures
- Empty value returns for missing QR codes
- Subprocess execution monitoring





### **Contact Us**

For any inquiries or questions, please contact us.

telegram : @topdev1012

email :  skymorning523@gmail.com

Teams :  https://teams.live.com/l/invite/FEA2FDDFSy11sfuegI