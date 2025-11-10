"""
Configuration module for PaddleOCR VL API
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Device Configuration
    device: str = Field(default="cpu", env="DEVICE")
    
    # Model Configuration
    use_doc_orientation_classify: bool = Field(default=False, env="USE_DOC_ORIENTATION_CLASSIFY")
    use_doc_unwarping: bool = Field(default=False, env="USE_DOC_UNWARPING")
    use_textline_orientation: bool = Field(default=False, env="USE_TEXTLINE_ORIENTATION")
    use_layout_detection: bool = Field(default=True, env="USE_LAYOUT_DETECTION")
    
    # API Configuration
    max_upload_size: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
