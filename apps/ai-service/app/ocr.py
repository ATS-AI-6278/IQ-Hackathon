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


# ---------------------------------------------------------------------------
# Relevant Keywords
# ---------------------------------------------------------------------------
KEYWORDS = [
    "invoice", "tax invoice", "bill", "receipt", "warranty", "guarantee",
    "certificate", "product", "model", "serial", "s/n", "sn", "brand",
    "date", "price", "amount", "total", "seller", "dealer", "customer",
    "refrigerator", "fridge", "washing machine", "washer", "dryer",
    "dishwasher", "television", "tv", "microwave", "oven", "laptop",
    "espresso", "air conditioner", "ac", "purifier", "vacuum", "order"
]


def load_image_from_any(image_input) -> Image.Image:
    """Accepts file path, PIL Image, bytes, or base64 data URL / raw base64 string."""
    if isinstance(image_input, Image.Image):
        img = image_input
    elif isinstance(image_input, (str, Path)) and os.path.exists(str(image_input)):
        img = Image.open(str(image_input))
    elif isinstance(image_input, str):
        # Base64 string
        if "," in image_input:
            image_input = image_input.split(",", 1)[1]
        decoded = base64.b64decode(image_input)
        img = Image.open(io.BytesIO(decoded))
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def upscale_image(img: Image.Image, min_width: int = 1800) -> Image.Image:
    w, h = img.size
    if w >= min_width:
        return img
    scale = min_width / w
    return img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)


def create_image_variants(img: Image.Image):
    """Produces original, high-contrast grayscale, and sharpened variants."""
    upscaled = upscale_image(img)
    variants = [("original", upscaled)]

    # Grayscale + high contrast
    gray = ImageOps.grayscale(upscaled)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.8)
    gray = ImageEnhance.Sharpness(gray).enhance(2.0)
    variants.append(("grayscale", gray))

    # Sharpened
    sharp = upscaled.filter(ImageFilter.UnsharpMask(radius=2, percent=180, threshold=3))
    sharp = ImageEnhance.Contrast(sharp).enhance(1.5)
    variants.append(("sharpened", sharp))

    return variants


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
    Main OCR pipeline:
    1. Loads and preprocesses image with optimal resolution
    2. Runs RapidOCR and optional Tesseract on primary variant
    3. If text is sparse, checks high-contrast variant
    4. Merges text and filters relevant lines
    5. Returns structured OCR evidence
    """
    img = load_image_from_any(image_input)
    upscaled = upscale_image(img, min_width=1200)

    rapid_items = run_rapid_ocr(upscaled)
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

    # If text is sparse, try contrast-enhanced variant
    if len(cleaned_rapid) < 5:
        gray = ImageOps.grayscale(upscaled)
        gray = ImageOps.autocontrast(gray, cutoff=1)
        gray = ImageEnhance.Contrast(gray).enhance(1.8)
        more_items = run_rapid_ocr(gray)
        for it in more_items:
            if it["confidence"] >= 0.35 and it["text"]:
                txt = it["text"].strip()
                if txt and txt not in seen_texts:
                    seen_texts.add(txt)
                    cleaned_rapid.append(it)
                    rapid_lines.append(txt)

    best_tesseract = run_tesseract_ocr(upscaled) if TESSERACT_AVAILABLE else ""

    rapid_full = "\n".join(rapid_lines)
    combined = rapid_full
    if best_tesseract:
        combined = f"{rapid_full}\n\n[Tesseract]\n{best_tesseract}".strip()

    relevant = find_relevant_lines(combined)

    return {
        "combined_text": combined,
        "relevant_lines": relevant,
        "ocr_items": cleaned_rapid,
        "engine_used": "RapidOCR" if RAPIDOCR_AVAILABLE else ("Tesseract" if TESSERACT_AVAILABLE else "None"),
        "image_size": {
            "width": img.size[0],
            "height": img.size[1],
        }
    }
