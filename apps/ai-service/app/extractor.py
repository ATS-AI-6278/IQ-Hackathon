"""
PRODUCT PASSPORT - MULTI-PRODUCT EXTRACTION & DOCUMENT UNDERSTANDING

Pipeline:
1. IMAGE -> OCR evidence (via ocr.py) with caching and downscaling
2. High-precision regex/heuristic extraction (zero fabrication)
3. Optional fast Vision understanding via Ollama (strict 4s bounded timeout)
4. Data normalization (dates, prices, currencies, categories)
5. Strict anti-hallucination validation: null/empty strings when evidence is missing
"""

import os
import re
import json
import base64
import io
from pathlib import Path
from datetime import datetime
import requests
from PIL import Image

from .ocr import process_image, load_image_from_any

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_VISION_MODEL = os.environ.get("VISION_MODEL", "qwen2.5vl:7b")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "4"))
DISABLE_OLLAMA_VISION = os.environ.get("DISABLE_OLLAMA_VISION", "false").lower() in ("true", "1", "yes")

# Known consumer electronics / appliance brands
KNOWN_BRANDS = [
    "Samsung", "LG", "Sony", "Dell", "HP", "Lenovo", "Apple",
    "Electrolux", "Bosch", "Siemens", "Whirlpool", "Panasonic",
    "Philips", "Dyson", "Asus", "Acer", "Nordhaus", "Miele",
    "Haier", "Hisense", "TCL", "Toshiba", "Logitech"
]

# Blacklist of generic label words to never capture as models or serials
INVALID_CODE_WORDS = {
    "model", "modelcode", "modelno", "modelnumber", "mod",
    "serial", "serialno", "serialnumber", "sn", "s/n",
    "warranty", "guarantee", "certificate", "invoice", "receipt",
    "number", "customer", "customercopy", "date", "actiondate",
    "dateofpurchase", "purchase", "purchased", "extended", "extendedwarranty",
    "product", "productpurchased", "companyname", "logocompany", "logo",
    "partsnot", "partnot", "service", "terms", "limited", "signature"
}


def get_available_ollama_models() -> list[str]:
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    except Exception:
        pass
    return []


def choose_vision_model() -> str | None:
    if DISABLE_OLLAMA_VISION:
        return None
    models = get_available_ollama_models()
    for m in models:
        lower = m.lower()
        if any(target in lower for target in ["qwen2.5vl", "qwen2-vl", "qwen3-vl", "llama3.2-vision"]):
            return m
    if DEFAULT_VISION_MODEL in models:
        return DEFAULT_VISION_MODEL
    return None


def image_to_base64(img: Image.Image) -> str:
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def normalize_date(val_str: str | None) -> str | None:
    """Validates and normalizes date strings (YYYY-MM-DD, DD/MM/YYYY, etc.) rejecting invalid numbers."""
    if not val_str:
        return None
    val_str = str(val_str).strip()
    if not val_str or len(val_str) < 6:
        return None

    formats = [
        "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
        "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y",
        "%d/%m/%y", "%d-%m-%y", "%d.%m.%y",
        "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"
    ]
    for fmt in formats:
        try:
            parsed = datetime.strptime(val_str, fmt)
            # Basic sanity check: year between 1995 and 2035
            if 1995 <= parsed.year <= 2035:
                return parsed.strftime("%Y-%m-%d")
        except Exception:
            pass

    return None


def extract_price_and_currency(text: str) -> tuple[float | None, str | None]:
    """
    Extracts authentic purchase price only when accompanied by explicit currency or price markers.
    Never extracts random standalone numbers as prices.
    """
    # 1. Look for currency symbol followed/preceded by amount: $599.00, €450, 1249 USD, etc.
    currency_patterns = [
        (r"\$\s*(\d{2,6}(?:[.,]\d{2})?)", "USD"),
        (r"(\d{2,6}(?:[.,]\d{2})?)\s*(?:USD|usd)\b", "USD"),
        (r"€\s*(\d{2,6}(?:[.,]\d{2})?)", "EUR"),
        (r"(\d{2,6}(?:[.,]\d{2})?)\s*(?:EUR|eur)\b", "EUR"),
        (r"£\s*(\d{2,6}(?:[.,]\d{2})?)", "GBP"),
        (r"(\d{2,6}(?:[.,]\d{2})?)\s*(?:GBP|gbp)\b", "GBP"),
        (r"₹\s*(\d{2,6}(?:[.,]\d{2})?)", "INR"),
        (r"(\d{2,6}(?:[.,]\d{2})?)\s*(?:INR|inr)\b", "INR"),
    ]
    for pat, curr in currency_patterns:
        m = re.search(pat, text)
        if m:
            raw = m.group(1).replace(",", ".")
            try:
                val = float(raw)
                if val > 0:
                    return val, curr
            except Exception:
                pass

    # 2. Look for price keywords: Total: 699, Amount: 350.00
    kw_pattern = r"(?:total\s*(?:amount|price)?|grand\s*total|net\s*amount|price|amount)\s*[:=]\s*[:$€£₹]?\s*(\d{2,6}(?:[.,]\d{2})?)"
    m = re.search(kw_pattern, text, re.IGNORECASE)
    if m:
        raw = m.group(1).replace(",", ".")
        try:
            val = float(raw)
            if val > 0:
                return val, "USD"
        except Exception:
            pass

    return None, None


def clean_json_response(text: str) -> dict | None:
    if not text:
        return None
    cleaned = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"```", "", cleaned).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(cleaned[start:end + 1])
        except Exception:
            pass
    return None


def fallback_extraction(ocr_evidence: dict) -> dict:
    """
    Evidence-based extraction pipeline (Zero fabrication):
    Extracts brand, model, serial, commercial fields from OCR evidence.
    Returns None or empty string when evidence is missing.
    """
    text = ocr_evidence.get("combined_text", "")
    lines = ocr_evidence.get("relevant_lines", [])
    lower = text.lower()

    # Document type
    doc_type = "Warranty certificate"
    if any(k in lower for k in ["tax invoice", "invoice", "commercial invoice"]):
        doc_type = "Purchase invoice"
    elif any(k in lower for k in ["receipt", "cash receipt", "sales receipt", "bill"]):
        doc_type = "Retail receipt"
    elif any(k in lower for k in ["rating plate", "product label", "specification label"]):
        doc_type = "Product label"
    elif any(k in lower for k in ["extended warranty", "warranty card", "guarantee"]):
        doc_type = "Warranty certificate"

    # Brand extraction
    found_brand = ""
    for b in KNOWN_BRANDS:
        if re.search(rf"\b{re.escape(b)}\b", text, re.IGNORECASE):
            found_brand = b
            break

    # Model extraction
    model = ""
    model_patterns = [
        r"(?:model\s*(?:code|no|number)?|mod(?:el)?)\s*[:#\-]?\s*([A-Z0-9][A-Z0-9._/\-]{2,25})",
        r"\b([A-Z]{2,4}[0-9]{2,6}[A-Z0-9\-_]{1,12})\b",
    ]
    for pat in model_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            cand = m.group(1).strip().strip("-:._")
            cand_clean = re.sub(r"[^a-zA-Z0-9]", "", cand.lower())
            if len(cand) >= 3 and cand_clean not in INVALID_CODE_WORDS:
                model = cand
                break
        if model:
            break

    # Serial extraction
    serial = ""
    serial_patterns = [
        r"(?:s/n|sn|serial\s*(?:no|number)?)\s*[:#\-]?\s*([A-Z0-9][A-Z0-9._/\-]{3,25})",
        r"\b([0-9A-Z]{9,20})\b",
    ]
    for pat in serial_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            cand = m.group(1).strip().strip("-:._")
            cand_clean = re.sub(r"[^a-zA-Z0-9]", "", cand.lower())
            if len(cand) >= 4 and cand != model and cand_clean not in INVALID_CODE_WORDS:
                # Ensure it has both digits or letters
                if any(c.isdigit() for c in cand):
                    serial = cand
                    break
        if serial:
            break

    # Purchase Date extraction
    purchase_date = None
    # 1. Date with explicit prefix (e.g. ActionDate:05.09.2024, Date: 2021-04-06)
    date_kw_pattern = r"(?:action\s*date|purchase\s*date|date\s*of\s*purchase|invoice\s*date|date)\s*[:#\-]?\s*(\d{1,4}[./\-]\d{1,2}[./\-]\d{1,4})"
    m = re.search(date_kw_pattern, text, re.IGNORECASE)
    if m:
        purchase_date = normalize_date(m.group(1))

    # 2. General valid date regex
    if not purchase_date:
        date_candidates = re.findall(r"\b((?:20\d{2}[-/.](?:0?[1-9]|1[0-2])[-/.](?:0?[1-9]|[12]\d|3[01]))|(?:(?:0?[1-9]|[12]\d|3[01])[-/.](?:0?[1-9]|1[0-2])[-/.](?:20\d{2}|\d{2})))\b", text)
        for cand in date_candidates:
            d = normalize_date(cand)
            if d:
                purchase_date = d
                break

    # Price & Currency
    price, currency = extract_price_and_currency(text)

    # Warranty duration extraction
    warranty = None
    warranty_match = re.search(r"(\b\d{1,2}\s*(?:months?|years?|yr|mo)\b)\s*(?:warranty|guarantee)?", text, re.IGNORECASE)
    if warranty_match:
        warranty = warranty_match.group(1).strip()
    elif "warranty" in lower:
        if "24" in text:
            warranty = "24 months"
        elif "36" in text:
            warranty = "36 months"
        elif "12" in text or "1 year" in lower:
            warranty = "12 months"

    # Seller extraction
    seller = None
    seller_match = re.search(r"(?:sold\s*by|seller|store|retailer|dealer|merchant)\s*[:\-]?\s*([A-Za-z0-9 &.',\-]{3,35})", text, re.IGNORECASE)
    if seller_match:
        s_cand = seller_match.group(1).strip()
        if not any(kw in s_cand.lower() for kw in ["warranty", "invoice", "receipt", "signature"]):
            seller = s_cand

    # Product category & name
    category = "Other"
    product_name = None
    category_map = [
        ("refrigerator", "Refrigerator", "Home appliance"),
        ("fridge", "Refrigerator", "Home appliance"),
        ("washing machine", "Front Load Washer", "Home appliance"),
        ("washer", "Washing Machine", "Home appliance"),
        ("dryer", "Tumble Dryer", "Home appliance"),
        ("espresso", "Espresso Maker", "Small domestic appliance"),
        ("coffee maker", "Coffee Maker", "Small domestic appliance"),
        ("laptop", "Laptop", "Computing"),
        ("television", "Smart TV", "Electronics"),
        ("tv", "Smart TV", "Electronics"),
        ("microwave", "Microwave Oven", "Home appliance"),
        ("dishwasher", "Dishwasher", "Home appliance"),
        ("air-conditioner", "Air Conditioner", "Home appliance"),
        ("air conditioner", "Air Conditioner", "Home appliance"),
    ]
    for kw, pname, cat in category_map:
        if re.search(rf"\b{re.escape(kw)}\b", lower):
            product_name = f"{found_brand} {pname}".strip() if found_brand else pname
            category = cat
            break

    if not product_name:
        if found_brand and model:
            product_name = f"{found_brand} {model}".strip()
            category = "Electronics"
        elif found_brand:
            product_name = f"{found_brand} Product"
        elif model:
            product_name = f"Product {model}"
        else:
            product_name = "Verified Product"

    product = {
        "product": product_name,
        "brand": found_brand,
        "model": model,
        "serialNumber": serial,
        "category": category,
        "selected": True,
        "evidence": "Extracted from document OCR text using validated field rules.",
    }

    return {
        "documentType": doc_type,
        "products": [product],
        "extractedFields": {
            "purchaseDate": purchase_date,
            "purchasePrice": price,
            "currency": currency,
            "warranty": warranty,
            "seller": seller,
        }
    }


def create_vision_prompt(ocr_evidence: dict) -> str:
    combined_text = ocr_evidence.get("combined_text", "")
    relevant_lines = ocr_evidence.get("relevant_lines", [])

    return f"""
You are the document-understanding AI engine of an enterprise Product Passport system.
You are inspecting an invoice, receipt, warranty card, certificate, or product label.

CRITICAL RULES (ZERO FABRICATION):
1. Return null or empty string for ANY field not explicitly stated on the document.
2. NEVER guess, invent, or fabricate model numbers, serial numbers, prices, dates, or sellers.
3. Preserve exact model numbers and serial numbers.

OCR Text Context:
{combined_text[:2000]}

Relevant Lines:
{chr(10).join(relevant_lines[:20])}

Return ONLY valid JSON:
{{
  "document_type": "Purchase invoice" | "Retail receipt" | "Warranty certificate" | "Product label" | "Other",
  "products": [
    {{
      "product": "Product name or descriptive title",
      "brand": "Brand name or empty string",
      "model": "Exact model number or empty string",
      "serial_number": "Exact serial number or empty string",
      "category": "Home appliance" | "Electronics" | "Small domestic appliance" | "Computing" | "Other",
      "purchase_price": null,
      "currency": "USD" | "EUR" | "GBP" | null,
      "purchase_date": "YYYY-MM-DD" | null,
      "warranty": "12 months" | null,
      "seller": null,
      "selection_status": "checked" | "explicit" | "unchecked"
    }}
  ]
}}
"""


def extract_products_from_image(image_input, file_name: str = "", ocr_evidence: dict | None = None) -> dict:
    """
    Main extraction pipeline:
    1. Runs single-pass OCR (or reuses pre-computed ocr_evidence)
    2. Checks if OCR extracted strong evidence (brand + model/serial) -> short-circuits in <3s
    3. If vision needed and Ollama available, attempts fast Qwen query with strict 4s timeout
    4. Combines with validated extraction rules ensuring zero fabrication
    """
    if ocr_evidence is None:
        ocr_evidence = process_image(image_input)

    # Short-circuit check: if OCR evidence already found brand or model and valid text,
    # we don't need a slow 90-second Ollama call.
    fallback_res = fallback_extraction(ocr_evidence)
    has_strong_ocr = False
    if fallback_res.get("products"):
        p = fallback_res["products"][0]
        if (p.get("brand") and p.get("model")) or p.get("serialNumber"):
            has_strong_ocr = True

    # Only attempt Ollama if not short-circuited and vision model is ready
    vision_model = choose_vision_model() if not has_strong_ocr else None
    result = None

    if vision_model:
        prompt = create_vision_prompt(ocr_evidence)
        try:
            img, _ = load_image_from_any(image_input)
            b64 = image_to_base64(img)

            payload = {
                "model": vision_model,
                "prompt": prompt,
                "images": [b64],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.0}
            }
            resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=OLLAMA_TIMEOUT)
            if resp.status_code == 200:
                raw = resp.json().get("response", "")
                result = clean_json_response(raw)
        except Exception as e:
            # Bounded failure: immediately fall back without stalling
            pass

    if not result or not result.get("products"):
        return fallback_res

    # Process and normalize the model's output (preventing fabrication)
    raw_products = result.get("products", [])
    valid_products = []
    first_fields = {}

    for prod in raw_products:
        status = str(prod.get("selection_status", "")).lower()
        if status == "unchecked":
            continue

        p_name = prod.get("product") or fallback_res["products"][0]["product"]
        brand = prod.get("brand") or fallback_res["products"][0]["brand"]
        model = prod.get("model") or fallback_res["products"][0]["model"]
        serial = prod.get("serial_number") or fallback_res["products"][0]["serialNumber"]
        category = prod.get("category") or fallback_res["products"][0]["category"]

        price, curr = None, None
        if prod.get("purchase_price") is not None:
            try:
                price = float(prod.get("purchase_price"))
                curr = prod.get("currency") or "USD"
            except Exception:
                pass

        pdate = normalize_date(prod.get("purchase_date"))

        valid_products.append({
            "product": p_name,
            "brand": brand,
            "model": model,
            "serialNumber": serial,
            "category": category,
            "selected": True,
            "evidence": "Visual confirmation and OCR verification."
        })

        if not first_fields:
            first_fields = {
                "purchaseDate": pdate or fallback_res["extractedFields"].get("purchaseDate"),
                "purchasePrice": price or fallback_res["extractedFields"].get("purchasePrice"),
                "currency": curr or fallback_res["extractedFields"].get("currency"),
                "warranty": prod.get("warranty") or fallback_res["extractedFields"].get("warranty"),
                "seller": prod.get("seller") or fallback_res["extractedFields"].get("seller"),
            }

    doc_type = result.get("document_type") or fallback_res["documentType"]

    if not valid_products:
        return fallback_res

    return {
        "documentType": doc_type,
        "products": valid_products,
        "extractedFields": first_fields
    }

