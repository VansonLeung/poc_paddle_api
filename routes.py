"""
API route handlers for PaddleOCR endpoints
"""
import logging
import traceback
from typing import Optional, Union
from fastapi import File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse

import json
import numpy as np

from config import settings
from services import model_service
from utils import (
    save_upload_file_tmp,
    decode_base64_to_file,
    encode_image_to_base64,
    cleanup_temp_file
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)



async def root():
    """Root endpoint - API information"""
    return {
        "message": "PaddleOCR VL API",
        "version": "1.0.0",
        "endpoints": {
            "ocr": "/ocr",
            "document_parser": "/doc_parser",
            "structure_recognition": "/structure",
            "upload": "/upload"
        }
    }


async def health_check():
    """Health check endpoint"""
    from config import settings
    return {"status": "healthy", "device": settings.device}


async def perform_ocr(
    file: Optional[UploadFile] = File(None, description="Image file to perform OCR on (PNG, JPG, JPEG, BMP)"),
    image_base64: Optional[str] = Form(None, description="Base64 encoded image string (alternative to file upload)"),
    lang: str = Form("en", description="OCR language code (e.g., 'en' for English, 'ch' for Chinese)"),
    use_doc_orientation_classify: Optional[bool] = Form(None, description="Enable document orientation classification"),
    use_doc_unwarping: Optional[bool] = Form(None, description="Enable document unwarping/dewarping"),
    use_textline_orientation: Optional[bool] = Form(None, description="Enable textline orientation correction"),
    text_det_limit_side_len: Optional[int] = Form(None, description="Maximum side length for text detection (pixels)"),
    text_det_limit_type: Optional[str] = Form(None, description="Limit type: 'max' or 'min'"),
    text_det_thresh: Optional[float] = Form(None, description="Binary threshold for text detection (0.0-1.0)"),
    text_det_box_thresh: Optional[float] = Form(None, description="Box threshold for text detection (0.0-1.0)"),
    text_det_unclip_ratio: Optional[float] = Form(None, description="Unclip ratio for text detection bounding boxes"),
    text_rec_score_thresh: Optional[float] = Form(None, description="Minimum confidence score for text recognition (0.0-1.0)"),
    return_word_box: Optional[bool] = Form(None, description="Return word-level bounding boxes instead of line-level"),
):
    """
    Perform Optical Character Recognition (OCR) on an image.
    
    This endpoint extracts text from images using PaddleOCR. It supports various image formats
    and multiple languages. You can upload a file directly or provide a base64-encoded image.
    
    **Request Parameters:**
    - **file**: Upload an image file (PNG, JPG, JPEG, BMP)
    - **image_base64**: Alternative to file upload - provide base64 encoded image
    - **lang**: Language code for OCR (default: "en")
      - "en": English, "ch": Chinese, "fr": French, "de": German, "es": Spanish, "pt": Portuguese, etc.
    
    **Advanced Options:**
    - **use_doc_orientation_classify**: Detect and correct document orientation
    - **use_doc_unwarping**: Dewarp/straighten curved or distorted documents
    - **use_textline_orientation**: Correct text line orientation
    - **text_det_limit_side_len**: Resize image if side exceeds this length
    - **text_det_thresh**: Binary threshold for text detection (default: 0.3)
    - **text_det_box_thresh**: Confidence threshold for detected boxes (default: 0.5)
    - **text_rec_score_thresh**: Minimum confidence for recognized text (default: 0.5)
    - **return_word_box**: Return word-level bounding boxes instead of line-level
    
    **Response Format:**
    ```json
    {
      "success": true,
      "results": [
        {
          "json": {
            "res": {
              "input_path": "/tmp/image.jpg",
              "page_index": null,
              "dt_polys": [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ...],
              "rec_texts": ["Extracted text 1", "Extracted text 2", ...],
              "rec_scores": [0.9876, 0.9543, ...],
              "rec_polys": [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ...],
              "rec_boxes": [[x1, y1, x2, y2], ...]
            }
          },
          "markdown": "Extracted text in markdown format"
        }
      ]
    }
    ```
    
    **Response Fields:**
    - **success**: Boolean indicating if OCR was successful
    - **results**: Array of result objects (one per page/image)
      - **json**: Detailed OCR results
        - **res**: OCR result data
          - **input_path**: Path to the processed input file
          - **page_index**: Page number (null for single images, 0-based for PDFs)
          - **dt_polys**: Text detection polygons (4-point coordinates for each detected text region)
          - **rec_texts**: Array of recognized text strings
          - **rec_scores**: Confidence scores (0.0-1.0) for each recognized text
          - **rec_polys**: Recognition polygons (refined bounding boxes)
          - **rec_boxes**: Bounding boxes in [x1, y1, x2, y2] format
      - **markdown**: OCR results formatted as markdown text
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:18200/ocr" \\
      -F "file=@document.jpg" \\
      -F "lang=en"
    ```
    
    **Error Responses:**
    - **400**: No image provided (missing both file and image_base64)
    - **500**: OCR processing error (with error details)
    """
    temp_file = None
    
    try:
        logger.info(f"OCR request received - file: {file.filename if file else 'None'}, lang: {lang}")
        
        # Handle file input
        if file:
            temp_file = await save_upload_file_tmp(file)
            logger.info(f"File saved to: {temp_file}")
        elif image_base64:
            temp_file = decode_base64_to_file(image_base64)
            logger.info(f"Base64 decoded and saved to: {temp_file}")
        else:
            logger.warning("No image provided in OCR request")
            raise HTTPException(status_code=400, detail="No image provided")
        
        # Get OCR model and perform prediction
        logger.info("Getting OCR model...")
        ocr = model_service.get_ocr_model(lang=lang)
        logger.info("Performing OCR prediction...")
        results = ocr.predict(temp_file)
        logger.info(f"OCR prediction completed, got {len(results)} result(s)")
        
        output_results = []
        for res in results:
            result_dict = {
                "json": res._to_json(),
                "markdown": res._to_markdown(),
            }
            output_results.append(result_dict)
        
        logger.info("OCR request completed successfully")
        return JSONResponse(content={
            "success": True,
            "results": output_results
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"OCR processing error: {str(e)}")
    
    finally:
        if temp_file:
            cleanup_temp_file(temp_file)
            logger.debug(f"Cleaned up temp file: {temp_file}")


async def parse_document(
    file: Optional[UploadFile] = File(None),
    file_base64: Optional[str] = Form(None),
    use_doc_orientation_classify: Optional[bool] = Form(None),
    use_doc_unwarping: Optional[bool] = Form(None),
    use_layout_detection: Optional[bool] = Form(None),
    use_chart_recognition: Optional[bool] = Form(None),
    layout_threshold: Optional[float] = Form(None),
    layout_nms: Optional[float] = Form(None),
    layout_unclip_ratio: Optional[float] = Form(None),
    layout_merge_bboxes_mode: Optional[str] = Form(None),
    use_queues: Optional[bool] = Form(None),
    prompt_label: Optional[str] = Form(None),
    format_block_content: Optional[bool] = Form(None),
    repetition_penalty: Optional[float] = Form(None),
    temperature: Optional[float] = Form(None),
    top_p: Optional[float] = Form(None),
    min_pixels: Optional[int] = Form(None),
    max_pixels: Optional[int] = Form(None),
):
    """
    Parse document using PaddleOCR-VL (Vision-Language Model).
    
    This endpoint performs advanced document parsing with layout detection, extracting structured
    content from documents including text blocks, tables, figures, titles, and other layout elements.
    Supports both images and PDFs.
    
    **Request Parameters:**
    - **file**: Upload a document file (PNG, JPG, JPEG, BMP, PDF)
    - **file_base64**: Alternative to file upload - provide base64 encoded file
    
    **Layout & Processing Options:**
    - **use_doc_orientation_classify**: Detect and correct document orientation (default: false)
    - **use_doc_unwarping**: Dewarp/straighten curved or distorted documents (default: false)
    - **use_layout_detection**: Enable layout detection to identify document structure (default: true)
    - **use_chart_recognition**: Enable chart/figure recognition (default: false)
    - **layout_threshold**: Confidence threshold for layout detection (0.0-1.0)
    - **layout_nms**: NMS (Non-Maximum Suppression) threshold for layout detection
    - **layout_unclip_ratio**: Unclip ratio for layout region expansion
    - **layout_merge_bboxes_mode**: Mode for merging bounding boxes
    
    **Content Processing Options:**
    - **format_block_content**: Format block content with proper structure (default: false)
    - **prompt_label**: Custom prompt label for content extraction
    - **use_queues**: Enable queue-based processing for large documents
    
    **Generation Parameters (for VL model):**
    - **repetition_penalty**: Penalty for repeated tokens in text generation (default: 1.0)
    - **temperature**: Sampling temperature for generation (default: 1.0, higher = more random)
    - **top_p**: Nucleus sampling parameter (default: 1.0)
    - **min_pixels**: Minimum image pixels for resizing
    - **max_pixels**: Maximum image pixels for resizing
    
    **Response Format:**
    ```json
    {
      "success": true,
      "results": [
        {
          "json": {
            "res": {
              "input_path": "/tmp/document.jpg",
              "page_index": null,
              "model_settings": {
                "use_doc_preprocessor": false,
                "use_layout_detection": true,
                "use_chart_recognition": false,
                "format_block_content": false
              },
              "parsing_res_list": [
                {
                  "block_label": "paragraph_title",
                  "block_content": "Document Title",
                  "block_bbox": [x1, y1, x2, y2],
                  "block_id": 0,
                  "block_order": 1
                },
                {
                  "block_label": "text",
                  "block_content": "Paragraph content...",
                  "block_bbox": [x1, y1, x2, y2],
                  "block_id": 1,
                  "block_order": 2
                }
              ],
              "layout_det_res": {
                "input_path": null,
                "page_index": null,
                "boxes": [
                  {
                    "cls_id": 17,
                    "label": "paragraph_title",
                    "score": 0.6941,
                    "coordinate": [x1, y1, x2, y2]
                  }
                ]
              }
            }
          },
          "markdown": {
            "markdown_images": {},
            "page_index": null,
            "input_path": "/tmp/document.jpg",
            "markdown_texts": "## Document Title\\n\\nParagraph content...",
            "page_continuation_flags": [false, true]
          }
        }
      ]
    }
    ```
    
    **Response Fields:**
    - **success**: Boolean indicating if parsing was successful
    - **results**: Array of result objects (one per page)
      - **json**: Detailed parsing results
        - **res**: Parsing result data
          - **input_path**: Path to the processed input file
          - **page_index**: Page number (null for single images)
          - **model_settings**: Settings used for parsing
          - **parsing_res_list**: List of detected layout blocks
            - **block_label**: Type of block (paragraph_title, text, table, figure, footer, etc.)
            - **block_content**: Extracted text content from the block
            - **block_bbox**: Bounding box [x1, y1, x2, y2] in pixels
            - **block_id**: Unique identifier for the block
            - **block_order**: Reading order of the block
          - **layout_det_res**: Raw layout detection results with bounding boxes and confidence scores
      - **markdown**: Document content in markdown format
        - **markdown_texts**: Full document text formatted as markdown
        - **markdown_images**: Dictionary of embedded images (if any)
        - **page_continuation_flags**: Indicates page breaks in multi-page documents
    
    **Block Label Types:**
    - `paragraph_title`: Section headings and titles
    - `text`: Regular paragraph text
    - `table`: Table content
    - `figure`: Images, diagrams, charts
    - `footer`: Footer content
    - `header`: Header content
    - `list`: Bulleted or numbered lists
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:18200/doc_parser" \\
      -F "file=@document.pdf" \\
      -F "use_layout_detection=true"
    ```
    
    **Error Responses:**
    - **400**: No file provided (missing both file and file_base64)
    - **500**: Document parsing error (with error details)
    """
    temp_file = None
    
    try:
        logger.info(f"Document parser request received - file: {file.filename if file else 'None'}")
        
        # Handle file input
        if file:
            temp_file = await save_upload_file_tmp(file)
            logger.info(f"File saved to: {temp_file}")
        elif file_base64:
            temp_file = decode_base64_to_file(file_base64)
            logger.info(f"Base64 decoded and saved to: {temp_file}")
        else:
            logger.warning("No file provided in document parser request")
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Get PaddleOCR-VL model and perform prediction
        logger.info("Getting PaddleOCR-VL model...")
        vl_model = model_service.get_paddleocr_vl_model()
        logger.info("Performing document parsing prediction...")
        results = vl_model.predict(
          temp_file,
          use_doc_orientation_classify=use_doc_orientation_classify,
          use_doc_unwarping=use_doc_unwarping,
          use_layout_detection=use_layout_detection,
          use_chart_recognition=use_chart_recognition,
          layout_threshold=layout_threshold,
          layout_nms=layout_nms,
          layout_unclip_ratio=layout_unclip_ratio,
          layout_merge_bboxes_mode=layout_merge_bboxes_mode,
          use_queues=use_queues,
          prompt_label=prompt_label,
          format_block_content=format_block_content,
          repetition_penalty=repetition_penalty,
          temperature=temperature,
          top_p=top_p,
          min_pixels=min_pixels,
          max_pixels=max_pixels,
        )
        logger.info(f"Document parsing completed, got {len(results)} result(s)")
        
        output_results = []
        for res in results:
            result_dict = {
                "json": res._to_json(),
                "markdown": res._to_markdown(),
            }
            output_results.append(result_dict)
        
        logger.info("Document parser request completed successfully")
        return JSONResponse(content={
            "success": True,
            "results": output_results,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document parsing error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Document parsing error: {str(e)}")
    
    finally:
        if temp_file:
            cleanup_temp_file(temp_file)
            logger.debug(f"Cleaned up temp file: {temp_file}")


async def recognize_structure(
    file: Optional[UploadFile] = File(None),
    file_base64: Optional[str] = Form(None),
    use_doc_orientation_classify: Optional[bool] = Form(None),
    use_doc_unwarping: Optional[bool] = Form(None),
    use_textline_orientation: Optional[bool] = Form(None),
    use_seal_recognition: Optional[bool] = Form(None),
    use_table_recognition: Optional[bool] = Form(None),
    use_formula_recognition: Optional[bool] = Form(None),
    use_chart_recognition: Optional[bool] = Form(None),
    use_region_detection: Optional[bool] = Form(None),
    layout_threshold: Optional[bool] = Form(None),
    layout_nms: Optional[bool] = Form(None),
    layout_unclip_ratio: Optional[Union[float, list, dict, None]] = Form(None),
    layout_merge_bboxes_mode: Optional[Union[str, dict, None]] = Form(None),
    text_det_limit_side_len: Optional[int] = Form(None),
    text_det_limit_type: Optional[str] = Form(None),
    text_det_thresh: Optional[float] = Form(None),
    text_det_box_thresh: Optional[float] = Form(None),
    text_det_unclip_ratio: Optional[float] = Form(None),
    text_rec_score_thresh: Optional[float] = Form(None),
    seal_det_limit_side_len: Optional[int] = Form(None),
    seal_det_limit_type: Optional[str] = Form(None),
    seal_det_thresh: Optional[float] = Form(None),
    seal_det_box_thresh: Optional[float] = Form(None),
    seal_det_unclip_ratio: Optional[float] = Form(None),
    seal_rec_score_thresh: Optional[float] = Form(None),
    use_wired_table_cells_trans_to_html: bool = Form(False),
    use_wireless_table_cells_trans_to_html: bool = Form(False),
    use_table_orientation_classify: bool = Form(True),
    use_ocr_results_with_table_cells: bool = Form(True),
    use_e2e_wired_table_rec_model: bool = Form(False),
    use_e2e_wireless_table_rec_model: bool = Form(True),
):
    """
    Recognize document structure using PP-StructureV3.
    
    This endpoint performs comprehensive document structure recognition, including layout analysis,
    table detection and recognition, formula recognition, seal detection, and OCR. It's designed
    for complex document processing with detailed structural information.
    
    **Request Parameters:**
    - **file**: Upload a document file (PNG, JPG, JPEG, BMP, PDF)
    - **file_base64**: Alternative to file upload - provide base64 encoded file
    
    **Document Preprocessing:**
    - **use_doc_orientation_classify**: Detect and correct document orientation
    - **use_doc_unwarping**: Dewarp/straighten curved or distorted documents
    - **use_textline_orientation**: Correct text line orientation
    
    **Feature Toggles:**
    - **use_seal_recognition**: Enable seal/stamp recognition (default: false)
    - **use_table_recognition**: Enable table structure recognition (default: true)
    - **use_formula_recognition**: Enable mathematical formula recognition (default: true)
    - **use_chart_recognition**: Enable chart/graph recognition (default: false)
    - **use_region_detection**: Enable region detection for layout (default: true)
    
    **Layout Detection Parameters:**
    - **layout_threshold**: Confidence threshold for layout detection
    - **layout_nms**: NMS threshold for layout region merging
    - **layout_unclip_ratio**: Expansion ratio for layout regions
    - **layout_merge_bboxes_mode**: Mode for merging adjacent bounding boxes
    
    **Text Detection Parameters:**
    - **text_det_limit_side_len**: Maximum side length for text detection (pixels)
    - **text_det_limit_type**: Limit type: 'max' or 'min'
    - **text_det_thresh**: Binary threshold for text detection (0.0-1.0)
    - **text_det_box_thresh**: Box confidence threshold (0.0-1.0)
    - **text_det_unclip_ratio**: Unclip ratio for text boxes
    - **text_rec_score_thresh**: Minimum confidence for text recognition (0.0-1.0)
    
    **Seal Recognition Parameters:**
    - **seal_det_limit_side_len**: Maximum side length for seal detection
    - **seal_det_limit_type**: Limit type for seal detection
    - **seal_det_thresh**: Binary threshold for seal detection
    - **seal_det_box_thresh**: Box threshold for seal detection
    - **seal_det_unclip_ratio**: Unclip ratio for seal boxes
    - **seal_rec_score_thresh**: Minimum confidence for seal recognition
    
    **Table Recognition Options:**
    - **use_wired_table_cells_trans_to_html**: Convert wired tables to HTML (default: false)
    - **use_wireless_table_cells_trans_to_html**: Convert wireless tables to HTML (default: false)
    - **use_table_orientation_classify**: Classify table orientation (default: true)
    - **use_ocr_results_with_table_cells**: Include OCR in table cells (default: true)
    - **use_e2e_wired_table_rec_model**: Use end-to-end model for wired tables (default: false)
    - **use_e2e_wireless_table_rec_model**: Use end-to-end model for wireless tables (default: true)
    
    **Response Format:**
    ```json
    {
      "success": true,
      "results": [
        {
          "json": {
            "res": {
              "input_path": "/tmp/document.jpg",
              "page_index": null,
              "model_settings": {
                "use_doc_preprocessor": true,
                "use_seal_recognition": false,
                "use_table_recognition": true,
                "use_formula_recognition": true,
                "use_chart_recognition": false,
                "use_region_detection": true,
                "format_block_content": false
              },
              "parsing_res_list": [
                {
                  "block_label": "paragraph_title",
                  "block_content": "Section Title",
                  "block_bbox": [x1, y1, x2, y2],
                  "block_id": 0,
                  "block_order": 1
                },
                {
                  "block_label": "text",
                  "block_content": "Paragraph text...",
                  "block_bbox": [x1, y1, x2, y2],
                  "block_id": 1,
                  "block_order": 2
                }
              ],
              "doc_preprocessor_res": {
                "input_path": null,
                "page_index": null,
                "model_settings": {
                  "use_doc_orientation_classify": false,
                  "use_doc_unwarping": false
                },
                "angle": -1
              },
              "layout_det_res": {
                "input_path": null,
                "page_index": null,
                "boxes": [
                  {
                    "cls_id": 2,
                    "label": "text",
                    "score": 0.9298,
                    "coordinate": [x1, y1, x2, y2]
                  }
                ]
              },
              "overall_ocr_res": {
                "input_path": null,
                "page_index": null,
                "model_settings": {
                  "use_doc_preprocessor": false,
                  "use_textline_orientation": true
                },
                "dt_polys": [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ...],
                "rec_texts": ["Text 1", "Text 2", ...],
                "rec_scores": [0.9876, 0.9543, ...],
                "rec_polys": [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ...],
                "rec_boxes": [[x1, y1, x2, y2], ...]
              }
            }
          },
          "markdown": {
            "markdown_images": {},
            "page_index": null,
            "input_path": "/tmp/document.jpg",
            "markdown_texts": "## Section Title\\n\\nParagraph text...",
            "page_continuation_flags": [false, true]
          }
        }
      ]
    }
    ```
    
    **Response Fields:**
    - **success**: Boolean indicating if structure recognition was successful
    - **results**: Array of result objects (one per page)
      - **json**: Detailed structure recognition results
        - **res**: Structure result data
          - **input_path**: Path to the processed input file
          - **page_index**: Page number (null for single images)
          - **model_settings**: Settings used for structure recognition
          - **parsing_res_list**: List of parsed structural blocks
            - **block_label**: Type (paragraph_title, text, table, figure, footer, etc.)
            - **block_content**: Extracted content from the block
            - **block_bbox**: Bounding box [x1, y1, x2, y2] in pixels
            - **block_id**: Unique block identifier
            - **block_order**: Reading order sequence
          - **doc_preprocessor_res**: Document preprocessing results (orientation, angle)
          - **layout_det_res**: Layout detection results with regions and confidence scores
          - **overall_ocr_res**: Complete OCR results for the entire document
            - **dt_polys**: Detection polygons for text regions
            - **rec_texts**: Recognized text strings
            - **rec_scores**: Confidence scores for each text
            - **rec_polys**: Recognition polygons (refined coordinates)
            - **rec_boxes**: Bounding boxes in [x1, y1, x2, y2] format
      - **markdown**: Document structure in markdown format
        - **markdown_texts**: Full document formatted as markdown
        - **markdown_images**: Dictionary of embedded images
        - **page_continuation_flags**: Page break indicators
    
    **Block Label Types:**
    - `paragraph_title`: Headings and section titles
    - `text`: Regular paragraph text
    - `table`: Table structures
    - `figure`: Images, diagrams, charts
    - `formula`: Mathematical formulas
    - `seal`: Stamps and seals
    - `header`: Page headers
    - `footer`: Page footers
    - `list`: Lists (bulleted/numbered)
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:18200/structure" \\
      -F "file=@document.pdf" \\
      -F "use_table_recognition=true" \\
      -F "use_formula_recognition=true"
    ```
    
    **Error Responses:**
    - **400**: No file provided (missing both file and file_base64)
    - **500**: Structure recognition error (with error details)
    """
    temp_file = None
    
    try:
        logger.info(f"Structure recognition request received - file: {file.filename if file else 'None'}")
        
        # Handle file input
        if file:
            temp_file = await save_upload_file_tmp(file)
            logger.info(f"File saved to: {temp_file}")
        elif file_base64:
            temp_file = decode_base64_to_file(file_base64)
            logger.info(f"Base64 decoded and saved to: {temp_file}")
        else:
            logger.warning("No file provided in structure recognition request")
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Get PP-StructureV3 model and perform prediction
        logger.info("Getting PP-StructureV3 model...")
        structure_model = model_service.get_pp_structure_model()
        logger.info("Performing structure recognition prediction...")
        results = structure_model.predict(temp_file)
        logger.info(f"Structure recognition completed, got {len(results)} result(s)")
        
        output_results = []
        for res in results:
            result_dict = {
                "json": res._to_json(),
                "markdown": res._to_markdown(),
            }
            output_results.append(result_dict)
        
        logger.info("Structure recognition request completed successfully")
        return JSONResponse(content={
            "success": True,
            "results": output_results,
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Structure recognition error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Structure recognition error: {str(e)}")
    
    finally:
        if temp_file:
            cleanup_temp_file(temp_file)
            logger.debug(f"Cleaned up temp file: {temp_file}")


async def upload_file_endpoint(file: UploadFile = File(...)):
    """
    Upload a file and get its base64 encoding
    
    Args:
        file: Uploaded file
        
    Returns:
        File information and base64 encoding
    """
    try:
        logger.info(f"File upload request received - filename: {file.filename}, content_type: {file.content_type}")
        
        # Save file temporarily
        temp_file = await save_upload_file_tmp(file)
        logger.info(f"File saved to: {temp_file}")
        
        # Encode to base64
        base64_str = encode_image_to_base64(temp_file)
        logger.info(f"File encoded to base64, size: {len(base64_str)} bytes")
        
        # Clean up
        cleanup_temp_file(temp_file)
        logger.debug(f"Cleaned up temp file: {temp_file}")
        
        logger.info("File upload completed successfully")
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(base64_str),
            "base64": base64_str
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")
