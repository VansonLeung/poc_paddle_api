"""
Complete API Test Suite
Tests all endpoints of the PaddleOCR VL API
"""
import requests
import json


API_URL = "http://localhost:18200"


def test_health():
    """Test health check endpoint"""
    print("🏥 Testing Health Check...")
    response = requests.get(f"{API_URL}/health")
    
    if response.status_code == 200:
        print("✅ Health check passed!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Health check failed: {response.status_code}")
    print()


def test_root():
    """Test root endpoint"""
    print("🏠 Testing Root Endpoint...")
    response = requests.get(f"{API_URL}/")
    
    if response.status_code == 200:
        print("✅ Root endpoint passed!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Root endpoint failed: {response.status_code}")
    print()


def test_ocr():
    """Test OCR endpoint with a sample URL"""
    print("📝 Testing OCR Endpoint...")
    sample_url = "https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/general_ocr_002.png"
    
    try:
        # Download image
        img_response = requests.get(sample_url, timeout=10)
        if img_response.status_code != 200:
            print(f"❌ Failed to download sample image")
            return
        
        # Test OCR
        files = {"file": ("test.png", img_response.content, "image/png")}
        data = {"lang": "en"}
        
        response = requests.post(f"{API_URL}/ocr", files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OCR test passed!")
            
            # Print extracted text
            for page_result in result.get("results", []):
                print("\n  Extracted text:")
                for ocr_result in page_result.get("ocr_results", [])[:3]:  # Show first 3
                    print(f"    - {ocr_result['text']}")
        else:
            print(f"❌ OCR test failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ OCR test error: {e}")
    print()


def test_doc_parser():
    """Test document parser endpoint"""
    print("📄 Testing Document Parser Endpoint...")
    sample_url = "https://ap4.www.vanportdev.com/aab.jpeg"
    
    try:
        # Download document
        doc_response = requests.get(sample_url, timeout=10)
        if doc_response.status_code != 200:
            print(f"❌ Failed to download sample document")
            return
        
        # Test document parser
        files = {"file": ("test.png", doc_response.content, "image/png")}
        
        response = requests.post(f"{API_URL}/doc_parser", files=files, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document parser test passed!")
            
            # Print summary
            for page_result in result.get("results", []):
                layout_result = page_result.get("layout_parsing_result", {})
                print(f"\n  Detected elements:")
                print(f"    - Blocks: {len(layout_result.get('blocks', []))}")
                print(f"    - Tables: {len(layout_result.get('tables', []))}")
                print(f"    - Figures: {len(layout_result.get('figures', []))}")
        else:
            print(f"❌ Document parser test failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Document parser test error: {e}")
    print()


def test_structure():
    """Test structure recognition endpoint"""
    print("📊 Testing Structure Recognition Endpoint...")
    sample_url = "https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/pp_structure_v3_demo.png"
    
    try:
        # Download document
        doc_response = requests.get(sample_url, timeout=600)
        if doc_response.status_code != 200:
            print(f"❌ Failed to download sample document")
            return
        
        # Test structure recognition
        files = {"file": ("test.png", doc_response.content, "image/png")}
        
        response = requests.post(f"{API_URL}/structure", files=files, timeout=600)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Structure recognition test passed!")
            
            # Print summary
            for page_result in result.get("results", []):
                structure = page_result.get("structure", {})
                print(f"\n  Structure elements:")
                print(f"    - Layout regions: {len(structure.get('layout', []))}")
                print(f"    - Tables: {len(structure.get('tables', []))}")
                print(f"    - Text blocks: {len(structure.get('text_blocks', []))}")
        else:
            print(f"❌ Structure recognition test failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Structure recognition test error: {e}")
    print()


def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("🚀 PaddleOCR VL API - Complete Test Suite")
    print("=" * 60)
    print()
    
    # Check if server is running
    try:
        requests.get(f"{API_URL}/health", timeout=5)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API server!")
        print(f"   Make sure the server is running at {API_URL}")
        print("   Run: python app.py")
        return
    
    # Run tests
    test_root()
    test_health()
    test_ocr()
    test_doc_parser()
    test_structure()
    
    print("=" * 60)
    print("✨ Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
