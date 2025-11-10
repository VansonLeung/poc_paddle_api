# PaddleOCR VL API - Project Structure

## 📁 Project Overview

```
poc_paddle_ocr_2/
├── app.py                      # Main FastAPI application
├── config.py                   # Configuration management
├── utils.py                    # Utility functions for file handling
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
├── .gitignore                 # Git ignore rules
│
├── README.md                   # Comprehensive documentation
├── QUICKSTART.md              # Quick start guide
│
├── Dockerfile                  # Docker image definition
├── docker-compose.yml         # Docker Compose configuration
├── start.sh                   # Linux/macOS startup script
├── start.bat                  # Windows startup script
│
└── examples/                   # Client example scripts
    ├── client_ocr.py          # OCR endpoint examples
    ├── client_doc_parser.py   # Document parser examples
    ├── client_structure.py    # Structure recognition examples
    └── test_all.py            # Complete API test suite
```

## 🎯 Key Components

### Core Application Files

#### **app.py** - Main API Server
- FastAPI application with CORS support
- 5 main endpoints:
  - `GET /` - Root/info endpoint
  - `GET /health` - Health check
  - `POST /ocr` - Text recognition
  - `POST /doc_parser` - Document parsing (PaddleOCR-VL)
  - `POST /structure` - Structure recognition (PP-StructureV3)
  - `POST /upload` - File upload utility
- Lazy model loading for faster startup
- Error handling and validation

#### **config.py** - Configuration Management
- Environment-based settings using Pydantic
- Server, device, and model configurations
- Customizable via `.env` file

#### **utils.py** - File Utilities
- File upload handling
- Base64 encoding/decoding
- Temporary file management
- Image processing helpers

### Example Clients

All client examples demonstrate:
- File upload method
- Base64 encoding method
- URL-based processing
- Error handling

#### **client_ocr.py**
Demonstrates OCR text recognition with:
- Language selection
- Bounding box extraction
- Confidence scores

#### **client_doc_parser.py**
Shows PaddleOCR-VL document parsing:
- Layout detection
- Element recognition
- Markdown output
- PDF processing

#### **client_structure.py**
Illustrates structure recognition:
- Table detection
- Layout analysis
- Text block extraction

#### **test_all.py**
Complete test suite for all endpoints

### Deployment Files

#### **Dockerfile**
- Python 3.10 slim base image
- System dependencies for PaddleOCR
- Health check configuration
- CPU-optimized (modify for GPU)

#### **docker-compose.yml**
- Single-service deployment
- Volume mounting for outputs
- Health monitoring
- Easy configuration via environment variables

#### **Startup Scripts**
- `start.sh` (Linux/macOS) - Automated setup and launch
- `start.bat` (Windows) - Windows equivalent

## 🔧 API Endpoints Summary

| Endpoint | Method | Purpose | Input |
|----------|--------|---------|-------|
| `/` | GET | API information | None |
| `/health` | GET | Health check | None |
| `/ocr` | POST | Text recognition | Image file or base64 |
| `/doc_parser` | POST | Document parsing | Image/PDF or base64 |
| `/structure` | POST | Structure recognition | Image/PDF or base64 |
| `/upload` | POST | File upload utility | File |

## 📦 Dependencies

### Core
- **paddleocr** - OCR models and pipelines
- **paddlepaddle** - Deep learning framework
- **fastapi** - Web framework
- **uvicorn** - ASGI server

### Utilities
- **Pillow** - Image processing
- **pydantic** - Data validation
- **python-multipart** - File upload support
- **aiofiles** - Async file operations

### Client Examples
- **requests** - HTTP client

## 🚀 Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python app.py

# Test all endpoints
python examples/test_all.py

# Run specific example
python examples/client_ocr.py
```

## 🐳 Docker Quick Start

```bash
# Build and run
docker-compose up

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

## 📝 Configuration Options

Set in `.env` file:

```bash
# Server
HOST=0.0.0.0
PORT=8000

# Device (cpu, gpu, gpu:0, etc.)
DEVICE=cpu

# Model options
USE_DOC_ORIENTATION_CLASSIFY=False
USE_DOC_UNWARPING=False
USE_TEXTLINE_ORIENTATION=False
USE_LAYOUT_DETECTION=True

# Limits
MAX_UPLOAD_SIZE=10485760  # 10MB
```

## 🔍 Supported Features

### PaddleOCR (OCR Endpoint)
- ✅ Multi-language text recognition (109+ languages)
- ✅ Bounding box detection
- ✅ Confidence scores
- ✅ PDF support
- ✅ Batch processing

### PaddleOCR-VL (Document Parser)
- ✅ Layout detection
- ✅ Element recognition (text, tables, figures)
- ✅ Markdown output
- ✅ Multi-page PDF support
- ✅ 109 languages

### PP-StructureV3 (Structure Recognition)
- ✅ Table structure recognition
- ✅ Layout analysis
- ✅ Text block extraction
- ✅ Hierarchical structure
- ✅ Markdown conversion

## 🎓 Learning Resources

### Examples Provided
1. **Basic OCR** - `client_ocr.py`
2. **Document Parsing** - `client_doc_parser.py`
3. **Structure Recognition** - `client_structure.py`
4. **Complete Test Suite** - `test_all.py`

### Documentation
- README.md - Full documentation
- QUICKSTART.md - Quick start guide
- Interactive API docs - http://localhost:8000/docs

### External Resources
- [PaddleOCR Official Docs](https://paddlepaddle.github.io/PaddleOCR/)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🛠️ Development Tips

### Adding New Endpoints
1. Define endpoint in `app.py`
2. Add request/response models
3. Implement processing logic
4. Add example in `examples/`
5. Update documentation

### Custom Model Loading
Modify model initialization in `get_*_model()` functions:
```python
def get_ocr_model():
    global _ocr_model
    if _ocr_model is None:
        from paddleocr import PaddleOCR
        _ocr_model = PaddleOCR(
            # Custom parameters here
            lang="ch",  # Chinese
            det_model_dir="path/to/model",
            # ...
        )
    return _ocr_model
```

### Testing
```bash
# Test specific endpoint
curl -X POST http://localhost:8000/ocr -F "file=@test.jpg"

# Run all tests
python examples/test_all.py

# Check health
curl http://localhost:8000/health
```

## 📊 Performance Considerations

- **First Request**: Slower due to model loading (30-60s)
- **Subsequent Requests**: Fast (models cached)
- **GPU**: 3-10x faster than CPU
- **Batch Processing**: Process multiple images in sequence
- **Memory**: ~2GB RAM for CPU, ~4GB VRAM for GPU

## 🔒 Production Considerations

For production deployment, add:
- Authentication (JWT, OAuth, API keys)
- Rate limiting
- Request validation
- Error logging (structured logging)
- Monitoring (Prometheus, Grafana)
- Load balancing (nginx, HAProxy)
- Database for request history
- Async job queue for long tasks

## 📄 License

This project uses PaddleOCR (Apache 2.0 License).

---

**Created**: 2025
**Purpose**: Proof of Concept - PaddleOCR VL API Server
**Status**: Ready for development and testing
