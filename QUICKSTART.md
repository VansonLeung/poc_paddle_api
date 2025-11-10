# Quick Start Guide

## Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install packages
pip install paddlepaddle  # or paddlepaddle-gpu for GPU
pip install -r requirements.txt
```

### Step 2: Configure (Optional)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env to customize settings
# nano .env
```

### Step 3: Start the Server

```bash
# Method 1: Direct run
python app.py

# Method 2: Use startup script
# On macOS/Linux:
chmod +x start.sh
./start.sh

# On Windows:
start.bat

# Method 3: Docker
docker-compose up
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## Test the API

### Quick Test

```bash
# Check health
curl http://localhost:8000/health

# Test with example (after server is running)
python examples/test_all.py
```

### Manual Test with Sample Image

```bash
# Test OCR
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@your_image.jpg" \
  -F "lang=en"

# Test Document Parser
curl -X POST "http://localhost:8000/doc_parser" \
  -F "file=@your_document.pdf"
```

## Common Issues

### Import Error: paddleocr not found
```bash
pip install paddleocr
```

### Import Error: fastapi not found
```bash
pip install -r requirements.txt
```

### Model Download Issues
On first run, PaddleOCR will download models automatically. This may take a few minutes. Make sure you have internet connection.

### GPU Not Working
Make sure you have:
1. CUDA installed (11.8+)
2. PaddlePaddle GPU version: `pip install paddlepaddle-gpu`
3. Set `DEVICE=gpu` in `.env`

## Next Steps

- Check out the [README.md](README.md) for detailed documentation
- Explore client examples in the `examples/` directory
- Read the interactive API docs at http://localhost:8000/docs
- Visit [PaddleOCR documentation](https://paddlepaddle.github.io/PaddleOCR/) for more info

## Support

Having issues? Check:
- [PaddleOCR FAQ](https://paddlepaddle.github.io/PaddleOCR/latest/FAQ.html)
- [PaddleOCR GitHub Issues](https://github.com/PaddlePaddle/PaddleOCR/issues)
