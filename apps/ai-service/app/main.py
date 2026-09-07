"""
FASTAPI AI SERVICE
Document analysis (RapidOCR + Qwen2.5-VL), product detection (YOLO + plate OCR),
and grounded household Q&A (Gemma 2).
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

from .ocr import RAPIDOCR_AVAILABLE, TESSERACT_AVAILABLE, warmup_ocr
from .detector import detect_product_from_image, get_yolo_model, get_custom_yolo_model, warmup_yolo
from .extractor import extract_products_from_image
from .llm import choose_gemma_model, choose_vision_model, list_ollama_models
from .household import ask_household


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    version="1.1.0",
    description="YOLO + RapidOCR + Qwen2.5-VL + Gemma 2 household reasoning.",
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
    content: str


class ProductIdentifyRequest(BaseModel):
    image: str
    fast: bool = False


class HouseholdAskRequest(BaseModel):
    question: str
    passports: list[dict] = Field(default_factory=list)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "verid-ai-engine"}


@app.get("/status")
def get_service_status():
    ollama_models = list_ollama_models()
    vision_model = choose_vision_model()
    gemma_model = choose_gemma_model()
    custom_model = get_custom_yolo_model()
    yolo_model = get_yolo_model()

    ocr_engine_name = "RapidOCR (ONNX)" if RAPIDOCR_AVAILABLE else ("Tesseract" if TESSERACT_AVAILABLE else "Unavailable")
    ocr_status = "connected" if (RAPIDOCR_AVAILABLE or TESSERACT_AVAILABLE) else "unavailable"

    vision_status = "connected" if vision_model else ("degraded" if ollama_models else "unavailable")
    vision_detail = (
        f"Qwen2.5-VL via Ollama · {vision_model}"
        if vision_model
        else ("Ollama running but no vision model pulled (qwen2.5vl:3b or :7b)" if ollama_models else "Ollama offline — OCR/YOLO still local")
    )

    gemma_status = "connected" if gemma_model else ("degraded" if ollama_models else "unavailable")
    gemma_detail = (
        f"Gemma household LLM · {gemma_model}"
        if gemma_model
        else ("Pull gemma2:2b (or gemma2:4b) for grounded Ask Hovira" if ollama_models else "Deterministic vault answers only")
    )

    yolo_status = "connected" if (custom_model is not None or yolo_model is not None) else "unavailable"
    details = []
    if custom_model:
        details.append("Fine-tuned appliances")
    if yolo_model:
        details.append("COCO")
    yolo_detail = f"Active: {' + '.join(details)}" if details else "Model file missing or PyTorch error"

    return {
        "backend": {
            "name": "Passport AI Engine",
            "status": "connected",
            "detail": "FastAPI · local YOLO/OCR · optional Ollama Qwen + Gemma",
        },
        "services": [
            {"name": "OCR engine", "status": ocr_status, "detail": f"{ocr_engine_name} text extraction"},
            {"name": "Vision model", "status": vision_status, "detail": vision_detail},
            {"name": "Household LLM", "status": gemma_status, "detail": gemma_detail},
            {"name": "Product detection", "status": yolo_status, "detail": yolo_detail},
        ],
    }


@app.post("/analyze-document")
def analyze_document_endpoint(req: DocumentAnalysisRequest):
    try:
        res = extract_products_from_image(req.content, file_name=req.fileName)
        count = len(res.get("extractedProducts", []))
        print(f"[AI] 📄 Document Extracted: {req.fileName} ({count} product(s) found)")
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")


@app.post("/identify-product")
def identify_product_endpoint(req: ProductIdentifyRequest):
    try:
        res = detect_product_from_image(req.image, fast=req.fast)
        product = res.get("detectedProduct")
        conf = res.get("confidence", 0.0)
        if product and product != "Unidentified Product" and conf > 0.25:
            print(f"[AI] 🎯 Detected: {product} ({int(conf * 100)}% conf)")
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product identification failed: {str(e)}")


@app.post("/ask-household")
def ask_household_endpoint(req: HouseholdAskRequest):
    try:
        res = ask_household(req.question, req.passports)
        print(f"[AI] 🧠 Answered query: \"{req.question[:60]}\"")
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Household ask failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
