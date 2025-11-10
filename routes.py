"""
API route handlers for PaddleOCR endpoints
"""
import logging
import traceback
from typing import Optional, Union
from fastapi import File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse

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
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    lang: str = Form("en"),
    use_doc_orientation_classify: Optional[bool] = Form(None),
    use_doc_unwarping: Optional[bool] = Form(None),
    use_textline_orientation: Optional[bool] = Form(None),
    text_det_limit_side_len: Optional[int] = Form(None),
    text_det_limit_type: Optional[str] = Form(None),
    text_det_thresh: Optional[float] = Form(None),
    text_det_box_thresh: Optional[float] = Form(None),
    text_det_unclip_ratio: Optional[float] = Form(None),
    text_rec_score_thresh: Optional[float] = Form(None),
    return_word_box: Optional[bool] = Form(None),
):
    """
    Perform OCR on an image
    
    Args:
        file: Uploaded image file (optional)
        image_base64: Base64 encoded image (optional)
        lang: Language for OCR (default: "en")
        use_doc_orientation_classify: Whether to use document orientation classification
        use_doc_unwarping: Whether to use document unwarping
        use_textline_orientation: Whether to use textline orientation correction
        text_det_limit_side_len: Limit side length for text detection
        text_det_limit_type: Limit type for text detection
        text_det_thresh: Text detection threshold
        text_det_box_thresh: Text detection box threshold
        text_det_unclip_ratio: Text detection unclip ratio
        text_rec_score_thresh: Text recognition score threshold
        return_word_box: Whether to return word-level bounding boxes
        
    Returns:
        OCR results with text and bounding boxes
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
        
        # Format results
        output_results = []
        for res in results:
            result_dict = {
                "input_path": res.get("input_path"),
                "page_index": res.get("page_index"),
                "ocr_results": []
            }
            
            # Extract text and boxes
            if "rec_texts" in res:
                for i, text in enumerate(res["rec_texts"]):
                    result_dict["ocr_results"].append({
                        "text": text,
                        "score": float(res["rec_scores"][i]) if "rec_scores" in res else None,
                        "bbox": res["dt_polys"][i].tolist() if "dt_polys" in res else None
                    })
            
            output_results.append(result_dict)
        
        logger.info(f"OCR request completed successfully")
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
    Parse document using PaddleOCR-VL
    
    Args:
        file: Uploaded file (image or PDF)
        file_base64: Base64 encoded file
        use_doc_orientation_classify: Whether to use document orientation classification
        use_doc_unwarping: Whether to use document unwarping
        use_layout_detection: Whether to use layout detection
        use_chart_recognition: Whether to use chart recognition
        layout_threshold: Layout detection threshold
        layout_nms: Layout detection NMS value
        layout_unclip_ratio: Layout detection unclip ratio
        layout_merge_bboxes_mode: Layout detection merge boxes mode
        use_queues: Whether to use queues for processing
        prompt_label: Prompt label for content extraction
        format_block_content: Whether to format block content
        repetition_penalty: Repetition penalty for text generation
        temperature: Temperature for text generation
        top_p: Top-p sampling for text generation
        min_pixels: Minimum pixels for image resizing
        max_pixels: Maximum pixels for image resizing
        
    Returns:
        Document parsing results with layout and content
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
        
        # Format results
        output_results = []
        for res in results:
            # Handle both dictionary and object responses
            if isinstance(res, dict):
                # Dictionary response format
                result_dict = {
                    "input_path": res.get("input_path"),
                    "page_index": res.get("page_index"),
                    "model_settings": res.get("model_settings", {}),
                    "layout_detection": {},
                    "parsing_results": []
                }
                

                # Extract layout detection results
                if "layout_det_res" in res and res["layout_det_res"]:
                    layout_det = res["layout_det_res"]
                    boxes = []
                    box_list = layout_det["boxes"]
                    
                    for box in box_list:
                        # Use getattr to handle both objects and dict-like objects
                        box_data = {
                            "label": box['label'],
                            "score": box['score'],
                            "coordinate": [float(c) for c in box['coordinate']]
                        }
                        boxes.append(box_data)
                    
                    result_dict["layout_detection"] = {
                        "input_path": layout_det['input_path'],
                        "page_index": layout_det['page_index'],
                        "boxes": boxes
                    }
                
                # Extract parsing results (text blocks with content)
                if "parsing_res_list" in res and res["parsing_res_list"]:
                    for block in res["parsing_res_list"]:
                        # Use getattr to handle both objects and dict-like objects
                        block_data = {
                            "label": block.label,
                            "content": block.content,
                            "bbox": block.bbox,
                        }
                        result_dict["parsing_results"].append(block_data)
                
            else:
                # Object response format (legacy)
                result_dict = {
                    "input_path": res.get("input_path"),
                    "page_index": res.get("page_index"),
                    "layout_parsing_result": {}
                }
                
                # Extract layout parsing results
                if hasattr(res, "layout_parsing_result"):
                    lpr = res.layout_parsing_result
                    result_dict["layout_parsing_result"] = {
                        "blocks": lpr.get("blocks", []),
                        "tables": lpr.get("tables", []),
                        "figures": lpr.get("figures", [])
                    }
                
                # Extract markdown if available
                if hasattr(res, "markdown"):
                    result_dict["markdown"] = {
                        "text": res.markdown.get("text", ""),
                        "has_images": bool(res.markdown.get("markdown_images"))
                    }
            
            output_results.append(result_dict)
        
        logger.info("Document parser request completed successfully")
        return JSONResponse(content={
            "success": True,
            "results": output_results
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
    Recognize document structure using PP-StructureV3
    
    Args:
        file: Uploaded file (image or PDF)
        file_base64: Base64 encoded file
        
    Returns:
        Structure recognition results
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
        
        # Format results
        output_results = []
        for res in results:
            # Handle both dictionary and object responses
            if isinstance(res, dict):
                # Dictionary response format
                result_dict = {
                    "input_path": res.get("input_path"),
                    "page_index": res.get("page_index"),
                    "model_settings": res.get("model_settings", {}),
                    "layout_detection": {},
                    "parsing_results": [],
                    "tables": [],
                    "formulas": [],
                    "charts": []
                }
                
                # Extract layout detection results
                if "layout_det_res" in res and res["layout_det_res"]:
                    layout_det = res["layout_det_res"]
                    boxes = []
                    # Handle boxes which might be objects or dicts
                    if hasattr(layout_det, "boxes"):
                        box_list = layout_det.boxes
                    elif isinstance(layout_det, dict) and "boxes" in layout_det:
                        box_list = layout_det["boxes"]
                    else:
                        box_list = []
                    
                    for box in box_list:
                        # Use getattr to handle both objects and dict-like objects
                        box_data = {
                            "label": getattr(box, "label", ""),
                            "score": float(getattr(box, "score", 0)),
                            "coordinate": [float(c) for c in getattr(box, "coordinate", [])]
                        }
                        boxes.append(box_data)
                    
                    result_dict["layout_detection"] = {
                        "boxes": boxes,
                        "box_count": len(boxes)
                    }
                
                # Extract text parsing results
                if "parsing_res_list" in res and res["parsing_res_list"]:
                    for block in res["parsing_res_list"]:
                        # Use getattr to handle both objects and dict-like objects
                        block_data = {
                            "label": getattr(block, "block_label", ""),
                            "content": getattr(block, "block_content", ""),
                            "bbox": getattr(block, "block_bbox", [])
                        }
                        result_dict["parsing_results"].append(block_data)
                
                # Extract tables if available
                if "table_res_list" in res and res["table_res_list"]:
                    result_dict["tables"] = res["table_res_list"]
                
                # Extract formulas if available
                if "formula_res_list" in res and res["formula_res_list"]:
                    result_dict["formulas"] = res["formula_res_list"]
                
                # Extract charts if available
                if "chart_res_list" in res and res["chart_res_list"]:
                    result_dict["charts"] = res["chart_res_list"]
                
            else:
                # Object response format (legacy)
                result_dict = {
                    "input_path": res.get("input_path"),
                    "page_index": res.get("page_index"),
                    "structure": {}
                }
                
                # Extract structure information
                if hasattr(res, "layout_parsing_result"):
                    lpr = res.layout_parsing_result
                    result_dict["structure"] = {
                        "layout": lpr.get("layout", []),
                        "tables": lpr.get("tables", []),
                        "text_blocks": lpr.get("text_blocks", [])
                    }
                
                # Extract markdown if available
                if hasattr(res, "markdown"):
                    result_dict["markdown"] = res.markdown.get("text", "")
            
            output_results.append(result_dict)
        
        logger.info("Structure recognition request completed successfully")
        return JSONResponse(content={
            "success": True,
            "results": output_results
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
