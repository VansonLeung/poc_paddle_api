"""
Service layer for managing PaddleOCR models
Handles model initialization, caching, and lifecycle
"""
import logging
import traceback
from typing import Optional
from config import settings

# Configure logging with level from settings
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))


class ModelService:
    """Singleton service for managing PaddleOCR models"""
    
    _instance = None
    _ocr_model = None
    _paddleocr_vl_model = None
    _pp_structure_model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
        return cls._instance
    
    def get_ocr_model(self, lang: Optional[str] = None):
        """
        Get or initialize PaddleOCR model
        
        Args:
            lang: Language code (default from settings or 'en')
            
        Returns:
            PaddleOCR model instance
        """
        try:
            if self._ocr_model is None:
                logger.info(f"Initializing PaddleOCR model with lang={lang or 'en'}, device={settings.device}")
                from paddleocr import PaddleOCR
                self._ocr_model = PaddleOCR(
                    use_doc_orientation_classify=settings.use_doc_orientation_classify,
                    use_doc_unwarping=settings.use_doc_unwarping,
                    use_textline_orientation=settings.use_textline_orientation,
                    device=settings.device,
                    lang=lang or "en"
                )
                logger.info("PaddleOCR model initialized successfully")
            return self._ocr_model
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR model: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def get_paddleocr_vl_model(self):
        """
        Get or initialize PaddleOCR-VL model
        
        Returns:
            PaddleOCRVL model instance
        """
        try:
            if self._paddleocr_vl_model is None:
                logger.info("Initializing PaddleOCR-VL model...")
                from paddleocr import PaddleOCRVL
                # Note: PaddleOCRVL doesn't accept device parameter directly
                self._paddleocr_vl_model = PaddleOCRVL(
                    use_doc_orientation_classify=settings.use_doc_orientation_classify,
                    use_doc_unwarping=settings.use_doc_unwarping,
                    use_layout_detection=settings.use_layout_detection
                )
                logger.info("PaddleOCR-VL model initialized successfully")
            return self._paddleocr_vl_model
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR-VL model: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def get_pp_structure_model(self):
        """
        Get or initialize PP-StructureV3 model
        
        Returns:
            PPStructureV3 model instance
        """
        try:
            if self._pp_structure_model is None:
                logger.info("Initializing PP-StructureV3 model...")
                from paddleocr import PPStructureV3
                # Note: PPStructureV3 doesn't accept device parameter directly
                self._pp_structure_model = PPStructureV3(
                    use_doc_orientation_classify=settings.use_doc_orientation_classify,
                    use_doc_unwarping=settings.use_doc_unwarping
                )
                logger.info("PP-StructureV3 model initialized successfully")
            return self._pp_structure_model
        except Exception as e:
            logger.error(f"Failed to initialize PP-StructureV3 model: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def clear_models(self):
        """Clear all cached models to free memory"""
        logger.info("Clearing all cached models")
        self._ocr_model = None
        self._paddleocr_vl_model = None
        self._pp_structure_model = None
        logger.info("All models cleared successfully")


# Global model service instance
model_service = ModelService()
