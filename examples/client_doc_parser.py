"""
Document Parser Client Example
Demonstrates how to call the PaddleOCR-VL document parser endpoint
"""
import requests
import base64
import json
from pathlib import Path


API_URL = "http://localhost:18200"


def parse_document_from_file(file_path: str):
    """
    Parse a document (image or PDF) from a local file
    
    Args:
        file_path: Path to the document file
    """
    url = f"{API_URL}/doc_parser"
    
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f)}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Document Parsing Success!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Print summary
        print("\n📊 Document Summary:")
        for page_result in result.get("results", []):
            page_idx = page_result.get("page_index")
            print(f"\n  Page {page_idx if page_idx is not None else 'N/A'}:")
            
            # Show layout info
            layout_result = page_result.get("layout_parsing_result", {})
            blocks = layout_result.get("blocks", [])
            tables = layout_result.get("tables", [])
            figures = layout_result.get("figures", [])
            
            print(f"    - Blocks: {len(blocks)}")
            print(f"    - Tables: {len(tables)}")
            print(f"    - Figures: {len(figures)}")
            
            # Show markdown preview
            if "markdown" in page_result:
                md_text = page_result["markdown"].get("text", "")
                preview = md_text[:200] + "..." if len(md_text) > 200 else md_text
                print(f"\n    Markdown Preview:\n    {preview}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def parse_document_from_base64(file_path: str):
    """
    Parse a document using base64 encoded file
    
    Args:
        file_path: Path to the document file
    """
    url = f"{API_URL}/doc_parser"
    
    # Encode file to base64
    with open(file_path, "rb") as f:
        file_base64 = base64.b64encode(f.read()).decode("utf-8")
    
    data = {
        "file_base64": file_base64
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Document Parsing Success (Base64)!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def parse_document_from_url(doc_url: str):
    """
    Download a document from URL and parse it
    
    Args:
        doc_url: URL of the document
    """
    # Download document
    doc_response = requests.get(doc_url)
    
    if doc_response.status_code != 200:
        print(f"❌ Failed to download document from {doc_url}")
        return
    
    url = f"{API_URL}/doc_parser"
    
    # Determine file extension from URL
    file_ext = Path(doc_url).suffix or ".png"
    files = {"file": (f"document{file_ext}", doc_response.content)}
    
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Document Parsing Success (from URL)!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def parse_pdf_document(pdf_path: str):
    """
    Parse a multi-page PDF document
    
    Args:
        pdf_path: Path to the PDF file
    """
    url = f"{API_URL}/doc_parser"
    
    with open(pdf_path, "rb") as f:
        files = {"file": (Path(pdf_path).name, f, "application/pdf")}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ PDF Parsing Success!")
        
        # Print summary for each page
        print("\n📄 PDF Summary:")
        for i, page_result in enumerate(result.get("results", []), 1):
            print(f"\n  Page {i}:")
            
            layout_result = page_result.get("layout_parsing_result", {})
            print(f"    - Elements detected: {len(layout_result.get('blocks', []))}")
            
            if "markdown" in page_result:
                md_text = page_result["markdown"].get("text", "")
                word_count = len(md_text.split())
                print(f"    - Word count: {word_count}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("🚀 PaddleOCR API Client - Document Parser Example\n")
    
    # Example 1: Parse from local file
    print("=" * 50)
    print("Example 1: Parse document from local file")
    print("=" * 50)
    # Replace with your document path
    # parse_document_from_file("path/to/your/document.png")
    
    # Example 2: Parse from base64
    print("\n" + "=" * 50)
    print("Example 2: Parse document from base64 encoding")
    print("=" * 50)
    # parse_document_from_base64("path/to/your/document.png")
    
    # Example 3: Parse from URL
    print("\n" + "=" * 50)
    print("Example 3: Parse document from URL")
    print("=" * 50)
    sample_url = "https://ap4.www.vanportdev.com/aab.jpeg"
    parse_document_from_url(sample_url)
    
    # Example 4: Parse PDF
    print("\n" + "=" * 50)
    print("Example 4: Parse PDF document")
    print("=" * 50)
    # parse_pdf_document("path/to/your/document.pdf")
    
    print("\n✨ Done!")
