"""
OCR ENGINE
Image preprocessing and multi-engine OCR (RapidOCR + optional Tesseract)
with relevant keyword line extraction for product passports.
"""

import os
import re
import json
import shutil
import base64
import io
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Tesseract Auto-detection
# ---------------------------------------------------------------------------
TESSERACT_AVAILABLE = False
pytesseract = None

try:
    import pytesseract as _pytess
    pytesseract = _pytess

    tess_candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
    ]
    custom_path_file = BASE_DIR / "tesseract_path.txt"
    if custom_path_file.exists():
        try:
            custom_p = custom_path_file.read_text(encoding="utf-8").strip()
            if custom_p:
                tess_candidates.insert(0, custom_p)
        except Exception:
            pass

    which_tess = shutil.which("tesseract")
    if which_tess:
        tess_candidates.append(which_tess)

    for cand in tess_candidates:
        if cand and os.path.exists(cand):
            pytesseract.pytesseract.tesseract_cmd = cand
            break

    try:
        ver = pytesseract.get_tesseract_version()
        if ver:
            TESSERACT_AVAILABLE = True
    except Exception:
        TESSERACT_AVAILABLE = False
except ImportError:
    TESSERACT_AVAILABLE = False


# ---------------------------------------------------------------------------
# RapidOCR Auto-detection
# ---------------------------------------------------------------------------
RAPIDOCR_AVAILABLE = False
_rapid_engine = None

try:
    from rapidocr_onnxruntime import RapidOCR
    _rapid_engine = RapidOCR()
    RAPIDOCR_AVAILABLE = True
except Exception:
    RAPIDOCR_AVAILABLE = False


import hashlib

# ---------------------------------------------------------------------------
# In-memory OCR Result Cache
# ---------------------------------------------------------------------------
_ocr_cache: dict[str, dict] = {}
MAX_CACHE_SIZE = 64


def warmup_ocr():
    """Pre-warms the RapidOCR ONNX engine with a blank tensor."""
    if RAPIDOCR_AVAILABLE and _rapid_engine is not None:
        try:
            import numpy as np
            dummy = np.zeros((64, 64, 3), dtype=np.uint8)
            _rapid_engine(dummy)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Relevant Keywords
# ---------------------------------------------------------------------------
KEYWORDS = [
    "invoice", "tax invoice", "bill", "receipt", "warranty", "guarantee",
    "certificate", "product", "model", "serial", "s/n", "sn", "brand",
    "date", "price", "amount", "total", "seller", "dealer", "customer",
    "refrigerator", "fridge", "washing machine", "washer", "dryer",
    "dishwasher", "television", "tv", "microwave", "oven", "laptop",
    "espresso", "air conditioner", "ac", "purifier", "vacuum", "order",
    "gst", "gstin", "rupee", "rs.", "inr", "filter", "serial no"
]


def load_image_from_any(image_input) -> tuple[Image.Image, str]:
    """Accepts file path, PIL Image, bytes, or base64 data URL / raw base64 string.
    Returns (PIL Image, image_hash)."""
    raw_bytes = None
    if isinstance(image_input, Image.Image):
        img = image_input
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        raw_bytes = buf.getvalue()
    elif isinstance(image_input, (str, Path)) and os.path.exists(str(image_input)):
        with open(str(image_input), "rb") as f:
            raw_bytes = f.read()
        img = Image.open(io.BytesIO(raw_bytes))
    elif isinstance(image_input, str):
        content = image_input.split(",", 1)[1] if "," in image_input else image_input
        raw_bytes = base64.b64decode(content)
        img = Image.open(io.BytesIO(raw_bytes))
    elif isinstance(image_input, bytes):
        raw_bytes = image_input
        img = Image.open(io.BytesIO(raw_bytes))
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    if img.mode != "RGB":
        img = img.convert("RGB")

    img_hash = hashlib.sha256(raw_bytes if raw_bytes else b"").hexdigest()
    return img, img_hash


def optimize_image_for_ocr(img: Image.Image, max_dim: int = 1024) -> Image.Image:
    """Downscales oversized images and slightly enhances contrast for fast, accurate OCR."""
    w, h = img.size
    # If already moderate resolution, keep native
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)
    elif max(w, h) < 600:
        scale = 600 / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)

    return img


def run_rapid_ocr(img: Image.Image):
    if not RAPIDOCR_AVAILABLE or _rapid_engine is None:
        return []
    try:
        import numpy as np
        arr = np.array(img)
        result, _ = _rapid_engine(arr)
        items = []
        if result:
            for item in result:
                if len(item) >= 3:
                    items.append({
                        "text": str(item[1]).strip(),
                        "confidence": float(item[2]),
                        "box": item[0]
                    })
        return items
    except Exception as e:
        print(f"RapidOCR execution warning: {e}")
        return []


def run_tesseract_ocr(img: Image.Image) -> str:
    if not TESSERACT_AVAILABLE or pytesseract is None:
        return ""
    try:
        text = pytesseract.image_to_string(img, lang="eng", config="--psm 6")
        return text.strip()
    except Exception:
        return ""


def find_relevant_lines(text: str) -> list[str]:
    relevant = []
    seen = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or len(line) < 3:
            continue
        lower = line.lower()
        if any(kw in lower for kw in KEYWORDS):
            if line not in seen:
                seen.add(line)
                relevant.append(line)
    return relevant


def process_image(image_input) -> dict:
    """
    Fast, single-pass OCR pipeline with content-hash caching:
    1. Loads image & computes content hash (returns cached if present)
    2. Bounds image resolution to <= 1024px
    3. Runs single-pass RapidOCR
    4. Filters relevant lines and returns evidence
    """
    img, img_hash = load_image_from_any(image_input)

    # Check LRU cache
    if img_hash in _ocr_cache:
        return _ocr_cache[img_hash]

    optimized = optimize_image_for_ocr(img, max_dim=1024)
    rapid_items = run_rapid_ocr(optimized)

    cleaned_rapid = []
    seen_texts = set()
    rapid_lines = []

    for it in rapid_items:
        if it["confidence"] >= 0.35 and it["text"]:
            txt = it["text"].strip()
            if txt and txt not in seen_texts:
                seen_texts.add(txt)
                cleaned_rapid.append(it)
                rapid_lines.append(txt)

    rapid_full = "\n".join(rapid_lines)
    combined = rapid_full

    # Optional Tesseract only if RapidOCR found zero lines
    if not rapid_lines and TESSERACT_AVAILABLE:
        tess = run_tesseract_ocr(optimized)
        if tess:
            combined = tess

    relevant = find_relevant_lines(combined)

    evidence = {
        "combined_text": combined,
        "relevant_lines": relevant,
        "ocr_items": cleaned_rapid,
        "engine_used": "RapidOCR" if RAPIDOCR_AVAILABLE else ("Tesseract" if TESSERACT_AVAILABLE else "None"),
        "image_size": {
            "width": img.size[0],
            "height": img.size[1],
        }
    }

    # Store in LRU cache
    if len(_ocr_cache) >= MAX_CACHE_SIZE:
        _ocr_cache.pop(next(iter(_ocr_cache)))
    _ocr_cache[img_hash] = evidence

    return evidence
