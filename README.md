# PaddleOCR VL API

A comprehensive REST API server for OCR (Optical Character Recognition), document parsing, and structure recognition using PaddleOCR's powerful vision-language models.

## Features

### Core Capabilities

- **🔤 OCR (Optical Character Recognition)**
  - Extract text from images with precise bounding boxes
  - Confidence scores for each detected text region
  - Support for 109+ languages
  - Advanced options: orientation classification, document unwarping, textline orientation
  - Word-level or line-level bounding boxes

- **📄 Document Parsing (PaddleOCR-VL)**
  - Vision-Language model for advanced document understanding
  - Layout detection with element classification (titles, paragraphs, tables, figures, headers, footers)
  - Structured content extraction with reading order
  - Markdown output for easy content processing
  - Chart and figure recognition
  - Multi-page PDF support

- **🏗️ Structure Recognition (PP-StructureV3)**
  - Comprehensive document structure analysis
  - Table detection and recognition (wired and wireless tables)
  - Mathematical formula recognition
  - Seal/stamp detection and recognition
  - Complete OCR integration with layout information
  - Hierarchical document structure parsing

### Technical Features

- **Multiple Input Methods**: Direct file upload, base64 encoding, or URL-based processing
- **Flexible Configuration**: Environment-based settings with sensible defaults
- **Model Caching**: Models loaded once and cached for performance
- **Batch Processing**: Handle multiple pages in PDF documents
- **GPU Support**: Optional CUDA acceleration for faster processing
- **RESTful API**: Standard HTTP endpoints with comprehensive documentation
- **Interactive Documentation**: Swagger UI and ReDoc for API exploration
- **Detailed Logging**: Configurable log levels for debugging and monitoring

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
   pip install -r requirements.txt
   pip install -r requirements-cpu.txt
   
   # For GPU version (CUDA 12.6)
   pip install -r requirements.txt
   pip install -r requirements-gpu.txt
   ```

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env to customize settings
   ```

## Quick Start

### Start the Server

**Option 1: Direct Python**
```bash
python app.py
```

**Option 2: Using startup scripts**
```bash
# Linux/Mac
bash start.sh

# Windows
start.bat
```

The server will start on `http://localhost:8000` by default (or the port specified in `.env`).

You should see output like:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### API Documentation

Once the server is running, comprehensive interactive API documentation is available:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API explorer with request/response examples
  - Try out endpoints directly from the browser
  - Complete parameter descriptions and response schemas
  
- **ReDoc**: http://localhost:8000/redoc
  - Clean, three-panel documentation layout
  - Detailed request/response examples
  - Search functionality

- **OpenAPI JSON**: http://localhost:8000/openapi.json
  - Raw OpenAPI 3.0 specification
  - Use with API clients, code generators, or testing tools

All endpoints include detailed documentation with:
- Complete parameter descriptions with types and defaults
- Comprehensive response format examples with actual JSON structures
- Field-by-field explanations for all response objects
- Usage examples with curl commands
- Error response codes and descriptions

## API Endpoints

### 1. Health Check
```bash
GET /health
```

Returns server health status and configuration.

**Response**:
```json
{
  "status": "healthy",
  "device": "cpu"
}
```

---

### 2. OCR - Text Recognition
```bash
POST /ocr
```

Extract text from images with detailed OCR results including detection polygons, recognized text, and confidence scores.

**Parameters**:
- `file`: Image file (multipart/form-data) - PNG, JPG, JPEG, BMP
- `image_base64`: Base64 encoded image (alternative to file upload)
- `lang`: Language code (default: "en")
  - Common: `en`, `ch`, `fr`, `de`, `es`, `pt`, `korean`, `japan`, etc.

**Advanced Options**:
- `use_doc_orientation_classify`: Detect and correct document orientation
- `use_doc_unwarping`: Dewarp/straighten curved documents
- `use_textline_orientation`: Correct text line orientation
- `text_det_limit_side_len`: Max side length for text detection
- `text_det_thresh`: Binary threshold for text detection (0.0-1.0)
- `text_det_box_thresh`: Box confidence threshold (0.0-1.0)
- `text_rec_score_thresh`: Min confidence for text recognition (0.0-1.0)
- `return_word_box`: Return word-level boxes instead of line-level

**Example**:
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@image.jpg" \
  -F "lang=en"
```

**Response Format**:
```json
{
  "success": true,
  "results": [
    {
      "json": {
        "res": {
          "input_path": "/tmp/image.jpg",
          "page_index": null,
          "dt_polys": [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ...],
          "rec_texts": ["Extracted text 1", "Extracted text 2", ...],
          "rec_scores": [0.9876, 0.9543, ...],
          "rec_polys": [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ...],
          "rec_boxes": [[x1, y1, x2, y2], ...]
        }
      },
      "markdown": "Extracted text in markdown format"
    }
  ]
}
```

---

### 3. Document Parser (PaddleOCR-VL)
```bash
POST /doc_parser
```

Advanced document parsing with layout detection, extracting structured content including text blocks, tables, figures, titles, and other layout elements.

**Parameters**:
- `file`: Image or PDF file (multipart/form-data)
- `file_base64`: Base64 encoded file (alternative to file upload)

**Layout & Processing Options**:
- `use_doc_orientation_classify`: Detect and correct document orientation
- `use_doc_unwarping`: Dewarp/straighten curved documents
- `use_layout_detection`: Enable layout detection (default: true)
- `use_chart_recognition`: Enable chart/figure recognition
- `layout_threshold`: Confidence threshold for layout detection
- `layout_nms`: NMS threshold for layout detection
- `layout_unclip_ratio`: Unclip ratio for layout regions
- `format_block_content`: Format block content with structure

**Generation Parameters**:
- `repetition_penalty`: Penalty for repeated tokens (default: 1.0)
- `temperature`: Sampling temperature (higher = more random)
- `top_p`: Nucleus sampling parameter
- `min_pixels`, `max_pixels`: Image resizing constraints

**Example**:
```bash
curl -X POST "http://localhost:8000/doc_parser" \
  -F "file=@document.pdf" \
  -F "use_layout_detection=true"
```

**Response Format**:
```json
{
  "success": true,
  "results": [
    {
      "json": {
        "res": {
          "input_path": "/tmp/document.jpg",
          "page_index": null,
          "model_settings": {
            "use_layout_detection": true,
            "use_chart_recognition": false
          },
          "parsing_res_list": [
            {
              "block_label": "paragraph_title",
              "block_content": "Document Title",
              "block_bbox": [x1, y1, x2, y2],
              "block_id": 0,
              "block_order": 1
            },
            {
              "block_label": "text",
              "block_content": "Paragraph content...",
              "block_bbox": [x1, y1, x2, y2],
              "block_id": 1,
              "block_order": 2
            }
          ],
          "layout_det_res": {
            "boxes": [
              {
                "cls_id": 17,
                "label": "paragraph_title",
                "score": 0.69,
                "coordinate": [x1, y1, x2, y2]
              }
            ]
          }
        }
      },
      "markdown": {
        "markdown_texts": "## Document Title\n\nParagraph content...",
        "markdown_images": {},
        "page_continuation_flags": [false, true]
      }
    }
  ]
}
```

**Block Label Types**: `paragraph_title`, `text`, `table`, `figure`, `footer`, `header`, `list`

---

### 4. Structure Recognition (PP-StructureV3)
```bash
POST /structure
```

Comprehensive document structure recognition including layout analysis, table detection, formula recognition, seal detection, and complete OCR results.

**Parameters**:
- `file`: Image or PDF file (multipart/form-data)
- `file_base64`: Base64 encoded file (alternative to file upload)

**Feature Toggles**:
- `use_seal_recognition`: Enable seal/stamp recognition
- `use_table_recognition`: Enable table structure recognition (default: true)
- `use_formula_recognition`: Enable mathematical formula recognition (default: true)
- `use_chart_recognition`: Enable chart/graph recognition
- `use_region_detection`: Enable region detection for layout (default: true)

**Preprocessing Options**:
- `use_doc_orientation_classify`: Detect document orientation
- `use_doc_unwarping`: Dewarp curved documents
- `use_textline_orientation`: Correct text line orientation

**Text & Layout Parameters**:
- `text_det_*`: Text detection parameters (thresh, box_thresh, unclip_ratio, etc.)
- `layout_*`: Layout detection parameters (threshold, nms, unclip_ratio, etc.)
- `seal_det_*`: Seal detection parameters

**Table Recognition**:
- `use_wired_table_cells_trans_to_html`: Convert wired tables to HTML
- `use_wireless_table_cells_trans_to_html`: Convert wireless tables to HTML
- `use_table_orientation_classify`: Classify table orientation
- `use_ocr_results_with_table_cells`: Include OCR in table cells
- `use_e2e_wired_table_rec_model`: Use end-to-end model for wired tables
- `use_e2e_wireless_table_rec_model`: Use end-to-end model for wireless tables

**Example**:
```bash
curl -X POST "http://localhost:8000/structure" \
  -F "file=@table_document.jpg" \
  -F "use_table_recognition=true" \
  -F "use_formula_recognition=true"
```

**Response Format**:
```json
{
  "success": true,
  "results": [
    {
      "json": {
        "res": {
          "input_path": "/tmp/document.jpg",
          "page_index": null,
          "model_settings": {
            "use_seal_recognition": false,
            "use_table_recognition": true,
            "use_formula_recognition": true,
            "use_region_detection": true
          },
          "parsing_res_list": [
            {
              "block_label": "paragraph_title",
              "block_content": "Section Title",
              "block_bbox": [x1, y1, x2, y2],
              "block_id": 0,
              "block_order": 1
            }
          ],
          "doc_preprocessor_res": {
            "angle": -1,
            "model_settings": {
              "use_doc_orientation_classify": false
            }
          },
          "layout_det_res": {
            "boxes": [
              {
                "cls_id": 2,
                "label": "text",
                "score": 0.93,
                "coordinate": [x1, y1, x2, y2]
              }
            ]
          },
          "overall_ocr_res": {
            "dt_polys": [...],
            "rec_texts": [...],
            "rec_scores": [...],
            "rec_polys": [...],
            "rec_boxes": [...]
          }
        }
      },
      "markdown": {
        "markdown_texts": "## Section Title\n\nParagraph text...",
        "markdown_images": {},
        "page_continuation_flags": [false, true]
      }
    }
  ]
}
```

**Block Label Types**: `paragraph_title`, `text`, `table`, `figure`, `formula`, `seal`, `header`, `footer`, `list`

---

### 5. File Upload
```bash
POST /upload
```

Upload a file and get its base64 encoding for later use with other endpoints.

**Parameters**:
- `file`: Any file (multipart/form-data)

**Example**:
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@image.jpg"
```

**Response**:
```json
{
  "success": true,
  "filename": "image.jpg",
  "content_type": "image/jpeg",
  "size": 12345,
  "base64": "base64_encoded_string..."
}
```

## Project Structure

```
.
├── app.py                  # Main application entry point
├── config.py              # Configuration management with pydantic-settings
├── models.py              # Pydantic request/response models
├── routes.py              # API endpoint handlers
├── services.py            # Model lifecycle management (singleton pattern)
├── utils.py               # File handling utilities
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── examples/             # Client example scripts
│   ├── client_ocr.py           # OCR endpoint examples
│   ├── client_doc_parser.py    # Document parser examples
│   └── client_structure.py     # Structure recognition examples
└── README.md             # This file
```

## Python Client Examples

The `examples/` directory contains comprehensive Python client examples demonstrating all API features:

**1. OCR Client (`examples/client_ocr.py`)**:
```bash
python examples/client_ocr.py
```
Demonstrates:
- OCR from local file
- OCR from base64 encoding
- OCR from URL (downloads and processes)
- Extracting text with confidence scores

**2. Document Parser Client (`examples/client_doc_parser.py`)**:
```bash
python examples/client_doc_parser.py
```
Demonstrates:
- Document parsing from local file
- Document parsing from base64 encoding
- Document parsing from URL
- Multi-page PDF parsing
- Extracting structured content (blocks, tables, figures)

**3. Structure Recognition Client (`examples/client_structure.py`)**:
```bash
python examples/client_structure.py
```
Demonstrates:
- Structure recognition from local file
- Structure recognition from base64 encoding
- Structure recognition from URL
- Table structure recognition
- Accessing detailed OCR and layout results

Each client example includes:
- Multiple input methods (file, base64, URL)
- Response parsing and display
- Summary statistics
- Error handling

## Configuration

Edit `.env` file to configure server settings. Copy from `.env.example` to get started:

```bash
cp .env.example .env
```

**Server Configuration**:
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `DEVICE`: Computation device - `cpu`, `gpu`, `gpu:0`, `gpu:1`, etc. (default: `cpu`)
- `LOG_LEVEL`: Logging level - `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default: `INFO`)

**OCR Default Settings**:
- `USE_DOC_ORIENTATION_CLASSIFY`: Enable document orientation classification (default: `false`)
- `USE_DOC_UNWARPING`: Enable document image unwarping/dewarping (default: `false`)
- `USE_TEXTLINE_ORIENTATION`: Enable text line orientation classification (default: `true`)

**Document Parser Default Settings**:
- `USE_LAYOUT_DETECTION`: Enable layout detection for VL model (default: `true`)
- `USE_CHART_RECOGNITION`: Enable chart/figure recognition (default: `false`)

**Other Settings**:
- `MAX_UPLOAD_SIZE`: Maximum file upload size in bytes (default: unlimited)

**Example `.env` file**:
```bash
HOST=0.0.0.0
PORT=18200
DEVICE=cpu
LOG_LEVEL=INFO

# OCR Settings
USE_DOC_ORIENTATION_CLASSIFY=false
USE_DOC_UNWARPING=false
USE_TEXTLINE_ORIENTATION=true

# Document Parser Settings
USE_LAYOUT_DETECTION=true
USE_CHART_RECOGNITION=false
```

## Models & Capabilities

This API integrates three powerful PaddleOCR models:

### 1. PaddleOCR (Base OCR Model)
- **Purpose**: General-purpose text detection and recognition
- **Capabilities**:
  - Text detection with polygon bounding boxes
  - Text recognition with confidence scores
  - Multi-language support (109+ languages)
  - Orientation classification and correction
  - Document unwarping for curved/distorted images
- **Use Case**: General OCR tasks, text extraction from images

### 2. PaddleOCR-VL (Vision-Language Model)
- **Purpose**: Advanced document understanding with layout analysis
- **Capabilities**:
  - Layout detection (13+ element types)
  - Structured content extraction
  - Reading order determination
  - Markdown generation
  - Chart and figure recognition
  - Multi-modal understanding (vision + language)
- **Use Case**: Document digitization, content extraction, structured data parsing

### 3. PP-StructureV3 (Document Structure Analysis)
- **Purpose**: Comprehensive document structure recognition
- **Capabilities**:
  - All OCR capabilities plus:
  - Table structure recognition (wired and wireless)
  - Mathematical formula recognition
  - Seal/stamp detection and recognition
  - Hierarchical document structure
  - Complete layout analysis with detailed metadata
- **Use Case**: Complex documents, forms, tables, scientific papers, business documents

**Model Loading**: Models are loaded on-demand (lazy loading) and cached in memory for subsequent requests, ensuring fast response times after the first use.

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

All endpoints return JSON responses with a consistent structure:

```json
{
  "success": true,
  "results": [
    {
      "json": {
        "res": {
          "input_path": "/tmp/file.jpg",
          "page_index": null,
          // ... detailed results specific to each endpoint
        }
      },
      "markdown": {
        "markdown_texts": "Formatted content in markdown",
        "markdown_images": {},
        "page_continuation_flags": [false, true]
      }
    }
  ]
}
```

**Common Fields**:
- `success`: Boolean indicating if the request was successful
- `results`: Array of result objects (one per page for multi-page documents)
  - `json`: Detailed structured results with all detected elements
  - `markdown`: Document content formatted as markdown (available for doc_parser and structure endpoints)

**Coordinate Format**:
- Bounding boxes use `[x1, y1, x2, y2]` format (top-left and bottom-right corners)
- Polygons use `[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]` format (4 corner points in clockwise order)
- All coordinates are in pixels relative to the original image

## Performance Tips

1. **GPU Acceleration**: Set `DEVICE=gpu:0` in `.env` for 3-10x faster processing
   ```bash
   # In .env
   DEVICE=gpu:0
   ```

2. **Model Caching**: Models are loaded on first use and cached in memory
   - First request: slower (model loading)
   - Subsequent requests: fast (model cached)
   - Keep the server running to maintain cache

3. **Batch Processing**: For multiple files, send requests sequentially to the same server instance
   - Reuses cached models
   - More efficient than starting/stopping server

4. **File Size Optimization**:
   - Keep images under 10MB for optimal performance
   - Resize very large images before upload
   - Use appropriate image compression (JPEG quality 85-95)

5. **Endpoint Selection**:
   - Use `/ocr` for simple text extraction (fastest)
   - Use `/doc_parser` for documents with complex layouts
   - Use `/structure` for tables, forms, and hierarchical content (most comprehensive)

6. **Logging Level**: Set `LOG_LEVEL=WARNING` in production to reduce I/O overhead
   ```bash
   LOG_LEVEL=WARNING  # Only log warnings and errors
   ```

## Usage Tips

### Choosing the Right Endpoint

**Use `/ocr` when**:
- You just need text extraction
- Simple images with text
- Speed is critical
- You don't need layout information

**Use `/doc_parser` when**:
- You need structured content (titles, paragraphs, etc.)
- Document has complex layout
- You want markdown output
- You need reading order information

**Use `/structure` when**:
- Document contains tables
- You need table structure recognition
- Document has mathematical formulas
- You need seals/stamps detected
- You want complete document structure analysis

### Working with Responses

**Accessing Text Content**:
```python
# OCR endpoint
for result in response['results']:
    texts = result['json']['res']['rec_texts']
    scores = result['json']['res']['rec_scores']
    
# Document parser / Structure endpoints
for result in response['results']:
    # Structured content
    for block in result['json']['res']['parsing_res_list']:
        print(f"{block['block_label']}: {block['block_content']}")
    
    # Markdown format
    markdown = result['markdown']['markdown_texts']
```

### Common Parameters

**Language Selection** (OCR endpoint):
```bash
# English
curl -X POST "http://localhost:8000/ocr" -F "file=@image.jpg" -F "lang=en"

# Chinese
curl -X POST "http://localhost:8000/ocr" -F "file=@image.jpg" -F "lang=ch"

# Multiple languages (auto-detect)
curl -X POST "http://localhost:8000/ocr" -F "file=@image.jpg" -F "lang=ch"
```

**Quality vs Speed** (adjustable thresholds):
```bash
# Higher quality (slower)
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@image.jpg" \
  -F "text_det_thresh=0.2" \
  -F "text_rec_score_thresh=0.7"

# Faster (lower precision)
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@image.jpg" \
  -F "text_det_thresh=0.5" \
  -F "text_rec_score_thresh=0.5"
```

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
