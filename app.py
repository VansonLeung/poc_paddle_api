"""
PaddleOCR VL API Server
Provides REST API endpoints for various OCR and document parsing tasks

Modular architecture:
- models.py: Pydantic request/response models
- services.py: Model initialization and management
- routes.py: API endpoint handlers
- config.py: Configuration management
- utils.py: File handling utilities
"""
import sys
import importlib.util

# Check if running in virtual environment
def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    for module_name in ['fastapi', 'paddleocr', 'pydantic']:
        if importlib.util.find_spec(module_name) is None:
            missing.append(module_name)
    
    if missing:
        print("❌ Error: Required dependencies not found!")
        print(f"   Missing: {', '.join(missing)}")
        print()
        print("🔧 To fix this issue:")
        print("   1. Make sure you have a virtual environment:")
        print("      python -m venv venv")
        print()
        print("   2. Activate the virtual environment:")
        print("      • Linux/Mac: source venv/bin/activate")
        print("      • Windows: venv\\Scripts\\activate")
        print()
        print("   3. Install dependencies:")
        print("      pip install -r requirements.txt")
        print()
        print("   OR use the startup script:")
        print("      • Linux/Mac: bash start.sh")
        print("      • Windows: start.bat")
        sys.exit(1)

check_dependencies()

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
import routes

# Configure root logger with level from settings
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        Configured FastAPI app instance
    """
    app = FastAPI(
        title="PaddleOCR VL API",
        description="API for OCR, document parsing, and structure recognition using PaddleOCR",
        version="1.0.0",
        docs_url="/docs",  # Default Swagger UI
        redoc_url="/redoc",  # ReDoc UI
        openapi_url="/openapi.json"  # OpenAPI schema
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    app.add_api_route("/", routes.root, methods=["GET"], tags=["Info"])
    app.add_api_route("/health", routes.health_check, methods=["GET"], tags=["Health"])
    app.add_api_route("/ocr", routes.perform_ocr, methods=["POST"], tags=["OCR"])
    app.add_api_route("/doc_parser", routes.parse_document, methods=["POST"], tags=["Document Parser"])
    app.add_api_route("/structure", routes.recognize_structure, methods=["POST"], tags=["Structure Recognition"])
    app.add_api_route("/upload", routes.upload_file_endpoint, methods=["POST"], tags=["Utilities"])
    
    # Add custom Swagger documentation routes
    from fastapi.openapi.docs import get_swagger_ui_html
    from fastapi.responses import JSONResponse
    
    @app.get("/api-doc", include_in_schema=False)
    async def custom_swagger_ui():
        """Custom Swagger UI endpoint at /api-doc"""
        return get_swagger_ui_html(
            openapi_url="/swagger.json",
            title=app.title + " - Swagger UI"
        )
    
    @app.get("/swagger.json", include_in_schema=False)
    async def custom_openapi():
        """Custom OpenAPI JSON endpoint at /swagger.json"""
        return JSONResponse(content=app.openapi())
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
