"""
Pydantic models for API request and response schemas
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class OCRRequest(BaseModel):
    """Request model for OCR endpoint"""
    image: str  # Base64 encoded image
    lang: Optional[str] = "en"


class OCRResponse(BaseModel):
    """Response model for OCR endpoint"""
    success: bool
    results: List[Dict[str, Any]]
    message: Optional[str] = None


class DocumentParserRequest(BaseModel):
    """Request model for document parser endpoint"""
    file: str  # Base64 encoded file
    file_type: str = "image"  # "image" or "pdf"


class DocumentParserResponse(BaseModel):
    """Response model for document parser endpoint"""
    success: bool
    results: List[Dict[str, Any]]
    message: Optional[str] = None


class StructureRecognitionRequest(BaseModel):
    """Request model for structure recognition endpoint"""
    file: str  # Base64 encoded file
    file_type: str = "image"  # "image" or "pdf"


class StructureRecognitionResponse(BaseModel):
    """Response model for structure recognition endpoint"""
    success: bool
    results: List[Dict[str, Any]]
    message: Optional[str] = None


class FileUploadResponse(BaseModel):
    """Response model for file upload endpoint"""
    success: bool
    filename: str
    content_type: Optional[str] = None
    size: int
    base64: str
