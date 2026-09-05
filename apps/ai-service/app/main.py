"""
FASTAPI AI SERVICE
Provides HTTP endpoints for Document Analysis, Physical Product Detection,
and Service Health Monitoring for the Verid Product Passport system.
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from contextlib import asynccontextmanager
from .ocr import RAPIDOCR_AVAILABLE, TESSERACT_AVAILABLE, warmup_ocr
from .detector import detect_product_from_image, get_yolo_model, get_custom_yolo_model, warmup_yolo
from .extractor import extract_products_from_image, choose_vision_model, get_available_ollama_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warms deep learning models (YOLO & OCR) at server boot."""
    try:
        warmup_yolo()
    except Exception as e:
        print(f"YOLO pre-warm warning: {e}")
    try:
        warmup_ocr()
    except Exception as e:
        print(f"OCR pre-warm warning: {e}")
    yield


app = FastAPI(
    title="Verid Product Passport AI Engine",
    version="1.0.0",
    description="Microservice providing YOLO appliance detection, RapidOCR text extraction, and Qwen2.5-VL document understanding.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DocumentAnalysisRequest(BaseModel):
    fileName: str
    fileType: str
    content: str  # Base64 data URL or raw base64 string


class ProductIdentifyRequest(BaseModel):
    image: str  # Base64 data URL or raw base64 string


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "verid-ai-engine"}


@app.get("/status")
def get_service_status():
    """Live status of OCR, Vision model, and Product detection."""
    ollama_models = get_available_ollama_models()
    vision_model = choose_vision_model()
    custom_model = get_custom_yolo_model()
    yolo_model = get_yolo_model()

    ocr_engine_name = "RapidOCR (ONNX)" if RAPIDOCR_AVAILABLE else ("Tesseract" if TESSERACT_AVAILABLE else "Regex/Heuristic")
    ocr_status = "connected" if (RAPIDOCR_AVAILABLE or TESSERACT_AVAILABLE) else "degraded"

    vision_status = "connected" if vision_model else ("pending" if len(ollama_models) > 0 else "offline")
    vision_detail = f"Ollama model: {vision_model}" if vision_model else ("Ollama running (no vision model pulled)" if ollama_models else "Ollama offline (using smart heuristic fallback)")

    yolo_status = "connected" if (custom_model is not None or yolo_model is not None) else "degraded"
    details = []
    if custom_model:
        details.append("Fine-tuned Custom Appliances")
    if yolo_model:
        details.append("COCO Foundation")
    yolo_detail = f"Active: {' + '.join(details)}" if details else "Model file missing or PyTorch error"

    return {
        "backend": {
            "name": "Passport AI Engine",
            "status": "connected",
            "detail": "FastAPI service active · dual HTTP/CLI bridge enabled",
        },
        "services": [
            {
                "name": "OCR engine",
                "status": ocr_status,
                "detail": f"{ocr_engine_name} text extraction ready",
            },
            {
                "name": "Vision model",
                "status": vision_status,
                "detail": vision_detail,
            },
            {
                "name": "Product detection",
                "status": yolo_status,
                "detail": yolo_detail,
            },
        ],
    }


@app.post("/analyze-document")
def analyze_document_endpoint(req: DocumentAnalysisRequest):
    try:
        result = extract_products_from_image(req.content, file_name=req.fileName)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")


@app.post("/identify-product")
def identify_product_endpoint(req: ProductIdentifyRequest):
    try:
        result = detect_product_from_image(req.image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product identification failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
