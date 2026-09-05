"""
TEST SUITE FOR VERID AI SERVICE
Tests:
1. Status endpoint logic
2. OCR engine on a sample image
3. Extractor pipeline
4. YOLO product detector on a sample image
"""

import os
import sys
import json
from pathlib import Path

# Add apps/ai-service to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.ocr import process_image, RAPIDOCR_AVAILABLE
from app.detector import detect_product_from_image, get_yolo_model
from app.extractor import extract_products_from_image
from app.main import get_service_status

SAMPLES_DIR = BASE_DIR.parent.parent / "samples"


def run_tests():
    print("=" * 60)
    print("VERID AI SERVICE VERIFICATION SUITE")
    print("=" * 60)

    # Test 1: Service Status
    print("\n[1] Testing System Status...")
    status = get_service_status()
    print("Status result:", json.dumps(status, indent=2))
    assert "backend" in status
    assert "services" in status
    print("✓ Status check passed.")

    # Test 2: YOLO Model Loading & Inference
    print("\n[2] Testing YOLO Appliance Detector...")
    yolo = get_yolo_model()
    print("YOLO loaded:", yolo is not None)

    sample_img = SAMPLES_DIR / "img.jpg"
    if sample_img.exists():
        detection = detect_product_from_image(sample_img)
        print("Detection result for img.jpg:")
        print(json.dumps(detection, indent=2))
        assert "detectedProduct" in detection
        assert "confidence" in detection
        assert "boundingBox" in detection
        print("✓ Detection test passed.")
    else:
        print("Sample img.jpg not found, skipping inference.")

    # Test 3: OCR Engine
    print("\n[3] Testing OCR Engine...")
    print("RapidOCR available:", RAPIDOCR_AVAILABLE)
    sample_doc = SAMPLES_DIR / "image1.png"
    if not sample_doc.exists():
        sample_doc = SAMPLES_DIR / "image.png"

    if sample_doc.exists():
        ocr_res = process_image(sample_doc)
        print(f"OCR text length: {len(ocr_res['combined_text'])} chars")
        print(f"Relevant lines found: {len(ocr_res['relevant_lines'])}")
        print("First 3 relevant lines:", ocr_res['relevant_lines'][:3])
        assert "combined_text" in ocr_res
        print("✓ OCR test passed.")

        # Test 4: Extractor Pipeline
        print("\n[4] Testing Document Extractor...")
        extracted = extract_products_from_image(sample_doc, file_name=sample_doc.name)
        print("Extractor result:")
        print(json.dumps(extracted, indent=2))
        assert "documentType" in extracted
        assert "products" in extracted
        assert len(extracted["products"]) > 0
        print("✓ Extractor test passed.")
    else:
        print("Sample document not found, skipping document tests.")

    print("\n" + "=" * 60)
    print("ALL AI TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
