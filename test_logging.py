"""
Test script to verify logging functionality
"""
import logging
import sys

# Configure logging to show all levels
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

print("=" * 60)
print("Testing logging functionality...")
print("=" * 60)

# Import modules to test their loggers
print("\n1. Testing services.py logging:")
from services import model_service

try:
    print("   Attempting to get OCR model...")
    model = model_service.get_ocr_model()
    print("   ✓ OCR model loaded successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n2. Testing routes.py logging:")
# We'll just import to see if logging is configured
import routes
print("   ✓ Routes module imported successfully")

print("\n" + "=" * 60)
print("Logging test completed!")
print("=" * 60)
