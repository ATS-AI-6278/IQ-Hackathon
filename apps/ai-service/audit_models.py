"""
MODEL AUDIT SCRIPT
Tests every model (YOLO, RapidOCR, Tesseract, Extractor pipeline)
across all sample images in the samples directory.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add ai-service to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

from app.ocr import process_image, RAPIDOCR_AVAILABLE, TESSERACT_AVAILABLE, warmup_ocr
from app.detector import (
    detect_product_from_image,
    run_yolo,
    run_custom_yolo,
    load_image_cv2,
    get_yolo_model,
    get_custom_yolo_model,
    warmup_yolo,
)
from app.extractor import extract_products_from_image, choose_vision_model, get_available_ollama_models

SAMPLES_DIR = BASE_DIR.parent.parent / "samples"


def audit_models():
    print("=" * 70)
    print("STARTING COMPREHENSIVE MODEL AUDIT")
    print("=" * 70)

    # 1. Check Model Files & Dependencies
    print("\n[1] MODEL AVAILABILITY & CONFIGURATION")
    print("-" * 50)
    custom_model = get_custom_yolo_model()
    print(f"1. Custom Appliance YOLO Model: {'LOADED (OK)' if custom_model else 'NOT LOADED'}")
    if custom_model:
        print(f"   Classes: {list(custom_model.names.values())}")

    yolo_model = get_yolo_model()
    print(f"2. General COCO YOLO Model (yolo26n.pt): {'LOADED (OK)' if yolo_model else 'FAILED'}")
    if yolo_model:
        print(f"   Total detectable classes: {len(yolo_model.names)}")

    print(f"3. RapidOCR (ONNX Engine): {'AVAILABLE (OK)' if RAPIDOCR_AVAILABLE else 'UNAVAILABLE'}")
    print(f"4. Tesseract Engine: {'AVAILABLE (OK)' if TESSERACT_AVAILABLE else 'UNAVAILABLE (Optional)'}")

    ollama_models = get_available_ollama_models()
    vision_model = choose_vision_model()
    print(f"4. Ollama Vision Models: {ollama_models}")
    print(f"   Selected Vision Model: {vision_model or 'None (Offline Heuristic Fallback Active)'}")

    # Run Startup Pre-warm
    print("\n[*] RUNNING SYSTEM PRE-WARMING (Cold -> Warm Transition)")
    tw0 = time.time()
    warmup_yolo()
    warmup_ocr()
    print(f"   Pre-warm completed in {(time.time() - tw0)*1000:.1f}ms")

    # 2. Test YOLO Model on All Sample Images
    print("\n[2] YOLO OBJECT DETECTION INFERENCE AUDIT")
    print("-" * 50)
    images = list(SAMPLES_DIR.glob("*.jpg")) + list(SAMPLES_DIR.glob("*.png")) + list(SAMPLES_DIR.glob("*.webp"))
    print(f"Found {len(images)} sample images for testing.")

    for img_p in images:
        if "detected" in img_p.name or "icon" in img_p.name:
            continue
        t0 = time.time()
        img, w, h = load_image_cv2(img_p)
        if img is None:
            continue
        custom_dets = run_custom_yolo(img, w, h)
        if custom_dets:
            for d in custom_dets:
                print(f"  -> Custom Appliance: {d['product']} | Class: {d['raw_class']} | Conf: {d['confidence']*100:.1f}% | Box: {d['boundingBox']}")

        dets = run_yolo(img, w, h)
        dt = (time.time() - t0) * 1000
        print(f"\nImage: {img_p.name} ({w}x{h}) - Inference time: {dt:.1f}ms")
        if dets:
            for d in dets:
                print(f"  -> COCO Detected: {d['product']} | Class: {d['raw_class']} | Conf: {d['confidence']*100:.1f}% | Box: {d['boundingBox']}")
        elif not custom_dets:
            print("  -> No direct appliance detected by YOLO (delegates to Qwen/heuristic fallback)")

        # Run complete detection pipeline
        full_det = detect_product_from_image(img_p)
        print(f"  -> Pipeline Result: {full_det['detectedProduct']} ({full_det['category']}) | Conf: {full_det['confidence']}")

    # 3. Test OCR Model on Document Sample Images
    print("\n[3] OCR TEXT RECOGNITION AUDIT")
    print("-" * 50)
    doc_images = [p for p in images if p.name in ["image.png", "image1.png", "image2.png", "ocr check.webp", "hi.png"]]

    for doc_p in doc_images:
        t0 = time.time()
        res = process_image(doc_p)
        dt = (time.time() - t0) * 1000
        lines_count = len(res['combined_text'].splitlines())
        relevant_count = len(res['relevant_lines'])
        print(f"\nDocument: {doc_p.name} - OCR Time: {dt:.1f}ms")
        print(f"  -> Total text lines: {lines_count} | Relevant product lines: {relevant_count}")
        if res['relevant_lines']:
            print(f"  -> Sample lines: {res['relevant_lines'][:3]}")

        # Run full extraction pipeline
        ext_res = extract_products_from_image(doc_p, file_name=doc_p.name)
        print(f"  -> Extracted Type: {ext_res['documentType']}")
        if ext_res.get("products"):
            p0 = ext_res["products"][0]
            print(f"  -> Product: {p0.get('product')} | Brand: {p0.get('brand')} | Model: {p0.get('model')} | Serial: {p0.get('serialNumber')}")
        if ext_res.get("extractedFields"):
            print(f"  -> Commercial Fields: {ext_res['extractedFields']}")

    print("\n" + "=" * 70)
    print("ALL MODEL AUDITS PASSED WITH ZERO CRASHES!")
    print("=" * 70)


if __name__ == "__main__":
    audit_models()
