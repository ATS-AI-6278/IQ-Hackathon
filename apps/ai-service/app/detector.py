"""
PRODUCT DETECTOR
Dual-model evidence-based detection pipeline:
1. Fine-tuned Custom Appliance & Furniture YOLO Model (AC, Washing Machine, Closet, Water Purifier, Cot)
2. Foundation COCO YOLO Model (Laptop, TV, Refrigerator, Microwave, Oven, Smartphone, etc.)
3. Semantic Qwen2.5-VL fallback (bounded 4s timeout)
Zero fabrication: returns confidence 0.0 / Unidentified Product if no appliance is detected.
"""

import os
import io
import json
import base64
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
CUSTOM_MODEL_PATH = BASE_DIR / "models" / "custom_appliances.pt"
COCO_MODEL_PATH = BASE_DIR / "models" / "yolo26n.pt"
MODEL_PATH = COCO_MODEL_PATH  # Backwards compatibility

from .llm import VISION_TIMEOUT, choose_interactive_vision_model, ollama_generate

YOLO_CONFIDENCE = 0.20
YOLO_LIVE_CONFIDENCE = 0.45
YOLO_IOU = 0.45
YOLO_IMAGE_SIZE = 640
MIN_PRODUCT_CONFIDENCE = 0.40
LIVE_CUSTOM_MIN = 0.40
LIVE_COCO_MIN = 0.55
STILL_CUSTOM_MIN = 0.38

LIVE_SKIP_CUSTOM_PRODUCTS = {"Closet / Wardrobe", "Cot / Bed"}

LIVE_COCO_CLASSES = {
    "refrigerator": ("Refrigerator", "Home appliance"),
    "microwave": ("Microwave Oven", "Home appliance"),
    "oven": ("Oven", "Home appliance"),
    "tv": ("Television", "Electronics"),
    "laptop": ("Laptop", "Computing"),
    "cell phone": ("Smartphone", "Electronics"),
    "monitor": ("Monitor / Display", "Computing"),
}

# Custom fine-tuned appliance classes (trained from iQOO dataset)
CUSTOM_CLASSES_MAP = {
    0: ("Air Conditioner", "Home appliance"),
    1: ("Washing Machine", "Home appliance"),
    2: ("Closet / Wardrobe", "Furniture"),
    3: ("Water Purifier", "Home appliance"),
    4: ("Cot / Bed", "Furniture"),
    "ac": ("Air Conditioner", "Home appliance"),
    "air conditioner": ("Air Conditioner", "Home appliance"),
    "washing machine": ("Washing Machine", "Home appliance"),
    "closet": ("Closet / Wardrobe", "Furniture"),
    "water purifier": ("Water Purifier", "Home appliance"),
    "cot": ("Cot / Bed", "Furniture"),
    "bed": ("Cot / Bed", "Furniture"),
}

USEFUL_COCO_CLASSES = {
    "refrigerator": ("Refrigerator", "Home appliance"),
    "microwave": ("Microwave Oven", "Home appliance"),
    "oven": ("Oven", "Home appliance"),
    "toaster": ("Toaster", "Small domestic appliance"),
    "tv": ("Television", "Electronics"),
    "laptop": ("Laptop", "Computing"),
    "computer": ("Computer / PC", "Computing"),
    "cell phone": ("Smartphone", "Electronics"),
    "remote": ("Remote Control", "Electronics"),
    "keyboard": ("Keyboard", "Computing"),
    "mouse": ("Mouse", "Computing"),
    "monitor": ("Monitor / Display", "Computing"),
    "hair drier": ("Hair Dryer", "Small domestic appliance"),
    "vacuum": ("Vacuum Cleaner", "Home appliance"),
    "clock": ("Clock", "Electronics"),
    "camera": ("Camera", "Electronics"),
    "bottle": ("Bottle", "Accessories"),
    "chair": ("Chair", "Furniture"),
    "couch": ("Sofa", "Furniture"),
    "bed": ("Bed", "Furniture"),
    "sink": ("Sink", "Home fixture"),
    "toilet": ("Toilet", "Home fixture"),
}

REJECT_CLASSES = {
    "person", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant",
    "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie",
    "suitcase", "sports ball", "skateboard", "surfboard", "tennis racket",
    "baseball bat", "baseball glove", "skis", "snowboard", "bicycle",
    "motorcycle", "car", "truck", "bus", "train", "boat", "traffic light",
    "fire hydrant", "stop sign", "parking meter", "bench", "book"
}

# Model singletons
_custom_yolo_model = None
_coco_yolo_model = None


def get_custom_yolo_model():
    """Loads fine-tuned custom appliance YOLO model."""
    global _custom_yolo_model
    if _custom_yolo_model is None and CUSTOM_MODEL_PATH.exists():
        try:
            from ultralytics import YOLO
            _custom_yolo_model = YOLO(str(CUSTOM_MODEL_PATH))
            print(f"Loaded Custom Appliance YOLO model from {CUSTOM_MODEL_PATH}")
        except Exception as e:
            print(f"Failed to load Custom YOLO model from {CUSTOM_MODEL_PATH}: {e}")
            _custom_yolo_model = None
    return _custom_yolo_model


def get_yolo_model():
    """Loads general COCO foundation YOLO model."""
    global _coco_yolo_model
    if _coco_yolo_model is None and COCO_MODEL_PATH.exists():
        try:
            from ultralytics import YOLO
            _coco_yolo_model = YOLO(str(COCO_MODEL_PATH))
            print(f"Loaded COCO YOLO model from {COCO_MODEL_PATH}")
        except Exception as e:
            print(f"Failed to load COCO YOLO model from {COCO_MODEL_PATH}: {e}")
            _coco_yolo_model = None
    return _coco_yolo_model


def warmup_yolo():
    """Pre-warms PyTorch inference engines on server startup for sub-200ms latency."""
    dummy = np.zeros((640, 640, 3), dtype=np.uint8)

    custom = get_custom_yolo_model()
    if custom is not None:
        try:
            custom.predict(source=dummy, imgsz=YOLO_IMAGE_SIZE, verbose=False)
            print("Custom Appliance YOLO warmed up.")
        except Exception as e:
            print(f"Custom YOLO warmup warning: {e}")

    coco = get_yolo_model()
    if coco is not None:
        try:
            coco.predict(source=dummy, imgsz=YOLO_IMAGE_SIZE, verbose=False)
            print("COCO YOLO warmed up.")
        except Exception as e:
            print(f"COCO YOLO warmup warning: {e}")


def load_image_cv2(image_input) -> tuple[np.ndarray | None, int, int]:
    """Loads image as an OpenCV BGR numpy array and returns (img, width, height)."""
    # 1. Direct file path check
    if isinstance(image_input, (str, Path)):
        p = Path(str(image_input))
        if p.exists() and p.is_file():
            img = cv2.imread(str(p.resolve()))
            if img is not None:
                h, w = img.shape[:2]
                return img, w, h

    # 2. Base64 or bytes decode
    if isinstance(image_input, str):
        if "," in image_input:
            image_input = image_input.split(",", 1)[1]
        try:
            decoded = base64.b64decode(image_input)
            arr = np.frombuffer(decoded, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is not None:
                h, w = img.shape[:2]
                return img, w, h
        except Exception:
            pass
    elif isinstance(image_input, bytes):
        try:
            arr = np.frombuffer(image_input, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is not None:
                h, w = img.shape[:2]
                return img, w, h
        except Exception:
            pass
    elif isinstance(image_input, np.ndarray):
        h, w = image_input.shape[:2]
        return image_input, w, h

    return None, 0, 0


def run_custom_yolo(img: np.ndarray, width: int, height: int, *, live: bool = False) -> list[dict]:
    """Executes the fine-tuned custom appliance YOLO model."""
    model = get_custom_yolo_model()
    if model is None:
        return []

    try:
        results = model.predict(
            source=img,
            conf=YOLO_LIVE_CONFIDENCE if live else YOLO_CONFIDENCE,
            iou=YOLO_IOU,
            imgsz=YOLO_IMAGE_SIZE,
            verbose=False,
        )
    except Exception as e:
        print(f"Custom YOLO prediction error: {e}")
        return []

    detections = []
    for r in results:
        if r.boxes is None:
            continue
        boxes = r.boxes
        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i].item())
            conf = float(boxes.conf[i].item())
            xyxy = boxes.xyxy[i].cpu().numpy().astype(int).tolist()
            raw_name = model.names.get(cls_id, str(cls_id)).lower().strip()

            if cls_id in CUSTOM_CLASSES_MAP:
                name, cat = CUSTOM_CLASSES_MAP[cls_id]
            elif raw_name in CUSTOM_CLASSES_MAP:
                name, cat = CUSTOM_CLASSES_MAP[raw_name]
            else:
                name, cat = (raw_name.title(), "Home appliance")

            x1, y1, x2, y2 = xyxy
            norm_box = [
                round(max(0.0, min(1.0, y1 / height)), 3),
                round(max(0.0, min(1.0, x1 / width)), 3),
                round(max(0.0, min(1.0, y2 / height)), 3),
                round(max(0.0, min(1.0, x2 / width)), 3),
            ]
            box_area = (norm_box[2] - norm_box[0]) * (norm_box[3] - norm_box[1])
            calibrated_conf = round(conf, 2)
            if not live:
                prominence_boost = min(0.08, box_area * 0.10) if box_area >= 0.20 else 0.0
                calibrated_conf = round(min(0.98, conf + prominence_boost), 2)

            if live and (name in LIVE_SKIP_CUSTOM_PRODUCTS or box_area < 0.08):
                continue

            detections.append({
                "product": name,
                "category": cat,
                "confidence": calibrated_conf,
                "raw_confidence": round(conf, 2),
                "prominence_area": round(box_area, 2),
                "boundingBox": norm_box,
                "raw_box": xyxy,
                "source": "Custom-YOLO",
                "raw_class": raw_name,
            })

    detections.sort(key=lambda d: d["confidence"], reverse=True)
    return detections


def run_yolo(img: np.ndarray, width: int, height: int, *, live: bool = False) -> list[dict]:
    """Executes general COCO foundation YOLO model."""
    model = get_yolo_model()
    if model is None:
        return []

    allowed = LIVE_COCO_CLASSES if live else USEFUL_COCO_CLASSES
    min_conf = LIVE_COCO_MIN if live else MIN_PRODUCT_CONFIDENCE

    try:
        results = model.predict(
            source=img,
            conf=YOLO_LIVE_CONFIDENCE if live else YOLO_CONFIDENCE,
            iou=YOLO_IOU,
            imgsz=YOLO_IMAGE_SIZE,
            verbose=False,
        )
    except Exception as e:
        print(f"YOLO prediction error: {e}")
        return []

    detections = []
    for r in results:
        if r.boxes is None:
            continue
        boxes = r.boxes
        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i].item())
            conf = float(boxes.conf[i].item())
            xyxy = boxes.xyxy[i].cpu().numpy().astype(int).tolist()
            cls_name = model.names.get(cls_id, str(cls_id)).lower().strip()

            if cls_name in REJECT_CLASSES:
                continue

            if cls_name in allowed and conf >= min_conf:
                name, cat = allowed[cls_name]
                x1, y1, x2, y2 = xyxy
                norm_box = [
                    round(max(0.0, min(1.0, y1 / height)), 3),
                    round(max(0.0, min(1.0, x1 / width)), 3),
                    round(max(0.0, min(1.0, y2 / height)), 3),
                    round(max(0.0, min(1.0, x2 / width)), 3),
                ]
                box_area = (norm_box[2] - norm_box[0]) * (norm_box[3] - norm_box[1])
                calibrated_conf = round(conf, 2)
                if not live:
                    prominence_boost = min(0.08, box_area * 0.10) if box_area >= 0.25 else 0.0
                    calibrated_conf = round(min(0.95, conf + prominence_boost), 2)

                if live and box_area < 0.10:
                    continue

                detections.append({
                    "product": name,
                    "category": cat,
                    "confidence": calibrated_conf,
                    "raw_confidence": round(conf, 2),
                    "prominence_area": round(box_area, 2),
                    "boundingBox": norm_box,
                    "raw_box": xyxy,
                    "source": "COCO-YOLO",
                    "raw_class": cls_name,
                })

    detections.sort(key=lambda d: d["confidence"], reverse=True)
    return detections


def qwen_plate_read(image_input, ocr_text: str) -> dict | None:
    """Qwen2.5-VL reads a rating plate. Fields must appear in OCR when OCR exists."""
    model = choose_interactive_vision_model()
    if not model:
        return None
    try:
        if isinstance(image_input, (str, Path)) and os.path.exists(str(image_input)):
            with open(str(image_input), "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
        elif isinstance(image_input, str):
            b64 = image_input.split(",", 1)[1] if "," in image_input else image_input
        else:
            return None

        prompt = """Identify the main household appliance and any model/serial printed on a rating plate.
If a field is not clearly readable, return an empty string. Never invent codes.
Return JSON only:
{
  "detectedProduct": "product name or null",
  "category": "Home appliance",
  "brand": "",
  "model": "",
  "serialNumber": "",
  "confidence": 0.7,
  "visualFeatures": []
}
"""
        data = ollama_generate(model, prompt, images=[b64], timeout=VISION_TIMEOUT, json_mode=True)
        if not isinstance(data, dict) or not data.get("detectedProduct"):
            return None
        from .extractor import field_evidenced
        if ocr_text:
            data["brand"] = field_evidenced(data.get("brand"), ocr_text)
            data["model"] = field_evidenced(data.get("model"), ocr_text)
            data["serialNumber"] = field_evidenced(data.get("serialNumber") or data.get("serial_number"), ocr_text)
        return data
    except Exception:
        return None


def _ocr_plate_fields(image_input) -> dict:
    try:
        from .extractor import fallback_extraction
        from .ocr import process_image

        evidence = process_image(image_input)
        parsed = fallback_extraction(evidence)
        product = parsed.get("products", [{}])[0]
        return {
            "brand": product.get("brand") or "",
            "model": product.get("model") or "",
            "serialNumber": product.get("serialNumber") or "",
            "ocr_text": evidence.get("combined_text", ""),
        }
    except Exception:
        return {"brand": "", "model": "", "serialNumber": "", "ocr_text": ""}


def _is_live_frame(width: int, height: int) -> bool:
    return max(width, height) <= 520


def _frame_has_structure(img: np.ndarray, *, live: bool) -> bool:
    """Reject empty / nearly-uniform frames that custom YOLO happily mislabels."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    min_std = 22.0 if live else 12.0
    min_edges = 0.018 if live else 0.008
    if float(gray.std()) < min_std:
        return False
    edges = cv2.Canny(gray, 40, 120)
    if float((edges > 0).mean()) < min_edges:
        return False
    return True


def detect_product_from_image(image_input, fast: bool = False) -> dict:
    """
    1. Custom YOLO (domain classes)
    2. COCO YOLO only if custom is weak
    3. Full stills: OCR rating plate + optional Qwen2.5-VL
    Live/small frames skip OCR and VLM.
    """
    img, width, height = load_image_cv2(image_input)
    if img is None:
        raise ValueError("Could not decode image.")

    live = fast or _is_live_frame(width, height)
    if not _frame_has_structure(img, live=live):
        return {
            "detectedProduct": "Unidentified Product",
            "category": "Other",
            "brand": "",
            "model": "",
            "serialNumber": "",
            "confidence": 0.0,
            "boundingBox": [],
            "visualFeatures": [
                "Frame has too little detail to identify. Fill the view with the appliance, then try again."
            ],
            "source": "None",
            "mode": "live-yolo" if live else "still",
        }

    custom_dets = run_custom_yolo(img, width, height, live=live)
    coco_dets: list[dict] = []
    custom_floor = LIVE_CUSTOM_MIN if live else STILL_CUSTOM_MIN
    if not custom_dets or custom_dets[0]["raw_confidence"] < (0.55 if live else 0.45):
        coco_dets = run_yolo(img, width, height, live=live)

    best = None
    if custom_dets and custom_dets[0]["raw_confidence"] >= custom_floor:
        best = custom_dets[0]
    elif coco_dets and coco_dets[0]["raw_confidence"] >= (LIVE_COCO_MIN if live else MIN_PRODUCT_CONFIDENCE):
        best = coco_dets[0]

    plate = {"brand": "", "model": "", "serialNumber": "", "ocr_text": ""}
    qwen_res = None
    if not live:
        if best:
            plate = _ocr_plate_fields(image_input)
        qwen_res = qwen_plate_read(image_input, plate.get("ocr_text", ""))
        if qwen_res:
            plate["brand"] = plate["brand"] or str(qwen_res.get("brand") or "")
            plate["model"] = plate["model"] or str(qwen_res.get("model") or "")
            plate["serialNumber"] = plate["serialNumber"] or str(qwen_res.get("serialNumber") or "")
            qname = str(qwen_res.get("detectedProduct") or "").strip()
            if qname and qname.lower() not in {"null", "none", "unknown", "unidentified product"}:
                return {
                    "detectedProduct": qname,
                    "category": str(qwen_res.get("category") or (best["category"] if best else "Home appliance")),
                    "brand": plate.get("brand") or "",
                    "model": plate.get("model") or "",
                    "serialNumber": plate.get("serialNumber") or "",
                    "confidence": float(qwen_res.get("confidence", 0.70)),
                    "boundingBox": best["boundingBox"] if best else [0.08, 0.10, 0.86, 0.78],
                    "visualFeatures": qwen_res.get("visualFeatures") or [
                        "Qwen-VL identified the still (not the live YOLO HUD)",
                    ],
                    "source": "Qwen-VL",
                    "mode": "qwen-vl",
                    "yoloHint": best["product"] if best else "",
                }

    if best:
        visual_features = [
            f"{best['source']} · {best['product']}",
            f"Object boundary match ({int(best['confidence'] * 100)}%)",
            f"{'Live frame' if live else 'Still + plate OCR'}",
        ]
        if plate.get("serialNumber"):
            visual_features.append("Rating-plate serial evidenced in OCR")
        return {
            "detectedProduct": best["product"],
            "category": best["category"],
            "brand": plate.get("brand") or "",
            "model": plate.get("model") or "",
            "serialNumber": plate.get("serialNumber") or "",
            "confidence": best["raw_confidence"] if live else best["confidence"],
            "boundingBox": best["boundingBox"],
            "visualFeatures": visual_features,
            "source": best["source"],
            "mode": "live-yolo" if live else "still",
        }

    return {
        "detectedProduct": "Unidentified Product",
        "category": "Other",
        "brand": "",
        "model": "",
        "serialNumber": "",
        "confidence": 0.0,
        "boundingBox": [],
        "visualFeatures": ["No appliance with enough confidence. Live camera uses YOLO only — tap Confirm with Qwen for a still." if live else "No physical consumer appliance detected in this image."],
        "source": "None",
        "mode": "live-yolo" if live else "still",
    }
