"""
Utility functions for file handling and processing
"""
import base64
import io
import os
import tempfile
from pathlib import Path
from typing import Union, Tuple
from PIL import Image
import aiofiles


async def save_upload_file_tmp(upload_file) -> str:
    """
    Save uploaded file to temporary location
    
    Args:
        upload_file: FastAPI UploadFile object
        
    Returns:
        Path to saved temporary file
    """
    suffix = Path(upload_file.filename).suffix
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        content = await upload_file.read()
        tmp_file.write(content)
        return tmp_file.name


def decode_base64_to_image(base64_str: str) -> Image.Image:
    """
    Decode base64 string to PIL Image
    
    Args:
        base64_str: Base64 encoded image string
        
    Returns:
        PIL Image object
    """
    # Remove data URL prefix if present
    if "base64," in base64_str:
        base64_str = base64_str.split("base64,")[1]
    
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    return image


def decode_base64_to_file(base64_str: str, output_dir: str = None) -> str:
    """
    Decode base64 string to file
    
    Args:
        base64_str: Base64 encoded file string
        output_dir: Directory to save the file
        
    Returns:
        Path to saved file
    """
    if "base64," in base64_str:
        base64_str = base64_str.split("base64,")[1]
    
    file_data = base64.b64decode(base64_str)
    
    # Create temporary file
    suffix = ".png"  # Default to PNG
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=output_dir) as tmp_file:
            tmp_file.write(file_data)
            return tmp_file.name
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_data)
            return tmp_file.name


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode image file to base64 string
    
    Args:
        image_path: Path to image file
        
    Returns:
        Base64 encoded string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def cleanup_temp_file(file_path: str):
    """
    Remove temporary file
    
    Args:
        file_path: Path to file to remove
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error removing temp file {file_path}: {e}")


async def read_file_as_bytes(file_path: str) -> bytes:
    """
    Read file as bytes asynchronously
    
    Args:
        file_path: Path to file
        
    Returns:
        File content as bytes
    """
    async with aiofiles.open(file_path, "rb") as f:
        return await f.read()
