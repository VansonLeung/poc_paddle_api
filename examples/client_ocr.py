"""
OCR Client Example
Demonstrates how to call the OCR endpoint
"""
import requests
import base64
import json
from pathlib import Path


API_URL = "http://localhost:18200"


def ocr_from_file(image_path: str, lang: str = "en"):
    """
    Perform OCR on a local image file
    
    Args:
        image_path: Path to the image file
        lang: Language code for OCR
    """
    url = f"{API_URL}/ocr"
    
    with open(image_path, "rb") as f:
        files = {"file": (Path(image_path).name, f, "image/jpeg")}
        data = {"lang": lang}
        
        response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ OCR Success!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Extract and print just the text
        print("\n📝 Extracted Text:")
        for page_result in result.get("results", []):
            for ocr_result in page_result.get("ocr_results", []):
                print(f"  - {ocr_result['text']} (confidence: {ocr_result['score']:.2f})")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def ocr_from_base64(image_path: str, lang: str = "en"):
    """
    Perform OCR using base64 encoded image
    
    Args:
        image_path: Path to the image file
        lang: Language code for OCR
    """
    url = f"{API_URL}/ocr"
    
    # Encode image to base64
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")
    
    data = {
        "image_base64": image_base64,
        "lang": lang
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ OCR Success (Base64)!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def ocr_from_url(image_url: str, lang: str = "en"):
    """
    Download an image from URL and perform OCR
    
    Args:
        image_url: URL of the image
        lang: Language code for OCR
    """
    # Download image
    img_response = requests.get(image_url)
    
    if img_response.status_code != 200:
        print(f"❌ Failed to download image from {image_url}")
        return
    
    url = f"{API_URL}/ocr"
    
    files = {"file": ("image.jpg", img_response.content, "image/jpeg")}
    data = {"lang": lang}
    
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ OCR Success (from URL)!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("🚀 PaddleOCR API Client - OCR Example\n")
    
    # Example 1: OCR from local file
    print("=" * 50)
    print("Example 1: OCR from local file")
    print("=" * 50)
    # Replace with your image path
    # ocr_from_file("path/to/your/image.jpg", lang="en")
    
    # Example 2: OCR from base64
    print("\n" + "=" * 50)
    print("Example 2: OCR from base64 encoding")
    print("=" * 50)
    # ocr_from_base64("path/to/your/image.jpg", lang="en")
    
    # Example 3: OCR from URL
    print("\n" + "=" * 50)
    print("Example 3: OCR from URL")
    print("=" * 50)
    sample_url = "https://ap4.www.vanportdev.com/aab.jpeg"
    ocr_from_url(sample_url, lang="en")
    
    print("\n✨ Done!")
