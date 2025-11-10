# PaddleOCR VL API

A comprehensive REST API server for OCR (Optical Character Recognition), document parsing, and structure recognition using PaddleOCR's powerful vision-language models.

## Features

- **OCR**: Extract text from images with bounding boxes and confidence scores
- **Document Parsing (PaddleOCR-VL)**: Advanced document understanding with layout detection and element recognition
- **Structure Recognition (PP-StructureV3)**: Parse complex documents with tables, layouts, and hierarchical structure
- **File Upload Support**: Handle both direct file uploads and base64-encoded inputs
- **Multiple Languages**: Support for 109+ languages
- **PDF Support**: Process multi-page PDF documents

## Installation

### Prerequisites

- Python 3.8-3.12
- CUDA 11.8+ (for GPU support, optional)

### Setup

1. **Clone or download this project**

2. **Create a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   # For CPU version
   pip install paddlepaddle
   pip install -r requirements.txt
   
   # For GPU version (CUDA 12.6)
   pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env to customize settings
   ```

## Quick Start

### Start the Server

```bash
python app.py
```

The server will start on `http://localhost:8000` by default.

### API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check
```bash
GET /health
```

### 2. OCR - Text Recognition
```bash
POST /ocr
```
Extract text from images with bounding boxes.

**Parameters**:
- `file`: Image file (multipart/form-data)
- `image_base64`: Base64 encoded image (optional)
- `lang`: Language code (default: "en")

**Example**:
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@image.jpg" \
  -F "lang=en"
```

### 3. Document Parser (PaddleOCR-VL)
```bash
POST /doc_parser
```
Advanced document parsing with layout detection and element recognition.

**Parameters**:
- `file`: Image or PDF file
- `file_base64`: Base64 encoded file (optional)

**Example**:
```bash
curl -X POST "http://localhost:8000/doc_parser" \
  -F "file=@document.pdf"
```

### 4. Structure Recognition (PP-StructureV3)
```bash
POST /structure
```
Recognize document structure including tables and layouts.

**Parameters**:
- `file`: Image or PDF file
- `file_base64`: Base64 encoded file (optional)

**Example**:
```bash
curl -X POST "http://localhost:8000/structure" \
  -F "file=@table_document.jpg"
```

### 5. File Upload
```bash
POST /upload
```
Upload a file and get its base64 encoding.

**Example**:
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@image.jpg"
```

## Python Client Examples

See the `examples/` directory for Python client examples:

```bash
# Run OCR example
python examples/client_ocr.py

# Run document parser example
python examples/client_doc_parser.py

# Run structure recognition example
python examples/client_structure.py
```

## Configuration

Edit `.env` file to configure:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEVICE`: Computation device (cpu, gpu, gpu:0, etc.)
- `USE_DOC_ORIENTATION_CLASSIFY`: Enable document orientation classification
- `USE_DOC_UNWARPING`: Enable document image unwarping
- `USE_TEXTLINE_ORIENTATION`: Enable text line orientation classification
- `USE_LAYOUT_DETECTION`: Enable layout detection (for VL model)
- `MAX_UPLOAD_SIZE`: Maximum file upload size in bytes

## Supported Languages

PaddleOCR supports 109+ languages. Common ones include:
- `en`: English
- `ch`: Chinese
- `fr`: French
- `german`: German
- `korean`: Korean
- `japan`: Japanese

And many more! Check [PaddleOCR documentation](https://paddlepaddle.github.io/PaddleOCR/) for the full list.

## Response Format

All endpoints return JSON responses in the following format:

```json
{
  "success": true,
  "results": [
    {
      "input_path": "file.jpg",
      "page_index": null,
      "ocr_results": [
        {
          "text": "Recognized text",
          "score": 0.95,
          "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        }
      ]
    }
  ]
}
```

## Performance Tips

1. **GPU Acceleration**: Set `DEVICE=gpu:0` in `.env` for faster processing
2. **Batch Processing**: Send multiple pages/images in sequence
3. **Model Caching**: Models are loaded on first use and cached
4. **File Size**: Keep uploaded files under 10MB for optimal performance

## Troubleshooting

### Import Errors
If you see import errors, make sure dependencies are installed:
```bash
pip install -r requirements.txt
```

### CUDA/GPU Issues
For GPU support, ensure:
- CUDA toolkit is installed (version 11.8+)
- Compatible NVIDIA drivers
- PaddlePaddle GPU version is installed

### Memory Issues
- Reduce batch size
- Process smaller images
- Use CPU instead of GPU if memory is limited

## Advanced Usage

### Using with Docker

A Docker setup can be created for easier deployment. Example Dockerfile:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```

### Custom Model Paths

You can specify custom model paths by modifying the model initialization in `app.py`.

## License

This project uses PaddleOCR which is licensed under Apache 2.0.

## References

- [PaddleOCR Official Documentation](https://paddlepaddle.github.io/PaddleOCR/)
- [PaddleOCR GitHub Repository](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR-VL Documentation](http://www.paddleocr.ai/latest/version3.x/pipeline_usage/PaddleOCR-VL.html)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues and questions:
- Check the [PaddleOCR FAQ](https://paddlepaddle.github.io/PaddleOCR/latest/FAQ.html)
- Open an issue in this repository
- Refer to PaddleOCR documentation

---

**Note**: This is a demo/proof-of-concept application. For production use, consider adding:
- Authentication/authorization
- Rate limiting
- Request validation
- Error logging
- Monitoring
- Load balancing
