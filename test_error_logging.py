"""
Test script to demonstrate error logging with stack traces
"""
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

print("=" * 60)
print("Testing Error Logging with Stack Traces")
print("=" * 60)

# Test 1: Successful OCR request
print("\n1. Testing successful OCR model initialization:")
try:
    from services import model_service
    model = model_service.get_ocr_model()
    logger.info("✓ OCR model loaded successfully")
except Exception as e:
    logger.error(f"✗ Failed to load OCR model: {e}")

# Test 2: Try to trigger an error in document parser
print("\n2. Testing document parser (expected to fail due to missing dependencies):")
try:
    vl_model = model_service.get_paddleocr_vl_model()
    logger.info("✓ PaddleOCR-VL model loaded successfully")
except Exception as e:
    logger.error(f"✗ Failed to load PaddleOCR-VL model")
    logger.error(f"Error message: {str(e)}")
    # The stack trace is already logged by the service

# Test 3: Try structure model
print("\n3. Testing structure recognition (expected to fail due to missing dependencies):")
try:
    structure_model = model_service.get_pp_structure_model()
    logger.info("✓ PP-StructureV3 model loaded successfully")
except Exception as e:
    logger.error(f"✗ Failed to load PP-StructureV3 model")
    logger.error(f"Error message: {str(e)}")
    # The stack trace is already logged by the service

print("\n" + "=" * 60)
print("Error logging test completed!")
print("=" * 60)
print("\nNote: Errors above are expected for PaddleOCR-VL and PP-StructureV3")
print("as they require additional dependencies not installed in this setup.")
