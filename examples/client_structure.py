"""
Structure Recognition Client Example
Demonstrates how to call the PP-StructureV3 structure recognition endpoint
"""
import requests
import base64
import json
from pathlib import Path


API_URL = "http://localhost:18200"


def recognize_structure_from_file(file_path: str):
    """
    Recognize document structure from a local file
    
    Args:
        file_path: Path to the document file
    """
    url = f"{API_URL}/structure"
    
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f)}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Structure Recognition Success!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Print summary
        print("\n📊 Structure Summary:")
        for page_result in result.get("results", []):
            page_idx = page_result.get("page_index")
            print(f"\n  Page {page_idx if page_idx is not None else 'N/A'}:")
            
            # Show structure info
            structure = page_result.get("structure", {})
            layout = structure.get("layout", [])
            tables = structure.get("tables", [])
            text_blocks = structure.get("text_blocks", [])
            
            print(f"    - Layout regions: {len(layout)}")
            print(f"    - Tables: {len(tables)}")
            print(f"    - Text blocks: {len(text_blocks)}")
            
            # Show markdown if available
            if "markdown" in page_result:
                md_text = page_result["markdown"]
                preview = md_text[:200] + "..." if len(md_text) > 200 else md_text
                print(f"\n    Markdown Preview:\n    {preview}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def recognize_structure_from_base64(file_path: str):
    """
    Recognize structure using base64 encoded file
    
    Args:
        file_path: Path to the document file
    """
    url = f"{API_URL}/structure"
    
    # Encode file to base64
    with open(file_path, "rb") as f:
        file_base64 = base64.b64encode(f.read()).decode("utf-8")
    
    data = {
        "file_base64": file_base64
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Structure Recognition Success (Base64)!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def recognize_structure_from_url(doc_url: str):
    """
    Download a document from URL and recognize its structure
    
    Args:
        doc_url: URL of the document
    """
    # Download document
    doc_response = requests.get(doc_url)
    
    if doc_response.status_code != 200:
        print(f"❌ Failed to download document from {doc_url}")
        return
    
    url = f"{API_URL}/structure"
    
    # Determine file extension from URL
    file_ext = Path(doc_url).suffix or ".png"
    files = {"file": (f"document{file_ext}", doc_response.content)}
    
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Structure Recognition Success (from URL)!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def recognize_table_structure(image_path: str):
    """
    Recognize table structure in a document
    
    Args:
        image_path: Path to the image containing a table
    """
    url = f"{API_URL}/structure"
    
    with open(image_path, "rb") as f:
        files = {"file": (Path(image_path).name, f)}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Table Structure Recognition Success!")
        
        # Print table information
        print("\n📋 Table Analysis:")
        for page_result in result.get("results", []):
            structure = page_result.get("structure", {})
            tables = structure.get("tables", [])
            
            if tables:
                print(f"  Found {len(tables)} table(s)")
                for i, table in enumerate(tables, 1):
                    print(f"\n  Table {i}:")
                    # Print table details if available
                    if isinstance(table, dict):
                        print(f"    - Rows: {table.get('rows', 'N/A')}")
                        print(f"    - Columns: {table.get('cols', 'N/A')}")
            else:
                print("  No tables detected")
            
            # Show markdown
            if "markdown" in page_result:
                md_text = page_result["markdown"]
                print(f"\n  Markdown output:\n{md_text[:500]}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("🚀 PaddleOCR API Client - Structure Recognition Example\n")
    
    # Example 1: Recognize from local file
    print("=" * 50)
    print("Example 1: Recognize structure from local file")
    print("=" * 50)
    # Replace with your document path
    # recognize_structure_from_file("path/to/your/document.png")
    
    # Example 2: Recognize from base64
    print("\n" + "=" * 50)
    print("Example 2: Recognize structure from base64 encoding")
    print("=" * 50)
    # recognize_structure_from_base64("path/to/your/document.png")
    
    # Example 3: Recognize from URL
    print("\n" + "=" * 50)
    print("Example 3: Recognize structure from URL")
    print("=" * 50)
    sample_url = "https://ap4.www.vanportdev.com/aab.jpeg"
    recognize_structure_from_url(sample_url)
    
    # Example 4: Recognize table structure
    print("\n" + "=" * 50)
    print("Example 4: Recognize table structure")
    print("=" * 50)
    # recognize_table_structure("path/to/your/table_image.png")
    
    print("\n✨ Done!")
