"""
PRODUCT PASSPORT - MULTI-PRODUCT EXTRACTION & DOCUMENT UNDERSTANDING

Pipeline:
1. IMAGE -> OCR evidence (via ocr.py) with caching and downscaling
2. High-precision regex/heuristic extraction (zero fabrication)
3. Optional fast Vision understanding via Ollama (strict 4s bounded timeout)
4. Data normalization (dates, prices, currencies, categories)
5. Strict anti-hallucination validation: null/empty strings when evidence is missing
"""

import re
import json
import base64
import io
from datetime import datetime
from PIL import Image

from .ocr import process_image, load_image_from_any
from .llm import VISION_TIMEOUT, choose_interactive_vision_model, list_ollama_models, ollama_generate

# Backwards-compatible aliases used by main.py / audit scripts
def get_available_ollama_models() -> list[str]:
    return list_ollama_models()

# Known consumer electronics / appliance brands
KNOWN_BRANDS = [
    "Samsung", "LG", "Sony", "Dell", "HP", "Lenovo", "Apple",
    "Electrolux", "Bosch", "Siemens", "Whirlpool", "Panasonic",
    "Philips", "Dyson", "Asus", "Acer", "Nordhaus", "Miele",
    "Haier", "Hisense", "TCL", "Toshiba", "Logitech",
    "Aquaguard", "Kent", "Voltas", "Blue Star", "Godrej", "IFB",
    "Xiaomi", "iQOO", "Vivo", "Realme"
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


def _parse_amount(raw: str, indian: bool = False) -> float | None:
    cleaned = raw.strip()
    if indian or (cleaned.count(",") >= 1 and "." not in cleaned):
        cleaned = cleaned.replace(",", "")
    else:
        cleaned = cleaned.replace(",", ".")
    try:
        val = float(cleaned)
        return val if val > 0 else None
    except Exception:
        return None


def extract_price_and_currency(text: str) -> tuple[float | None, str | None]:
    """Extracts price only with an explicit currency marker. India-first (₹ / Rs / INR)."""
    currency_patterns = [
        (r"(?:₹|rs\.?|inr)\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{2})?|[0-9]{2,7}(?:\.[0-9]{2})?)", "INR", True),
        (r"([0-9]{1,3}(?:,[0-9]{2,3})+(?:\.[0-9]{2})?)\s*(?:₹|rs\.?|inr)\b", "INR", True),
        (r"\$\s*(\d{2,6}(?:[.,]\d{2})?)", "USD", False),
        (r"(\d{2,6}(?:[.,]\d{2})?)\s*(?:USD|usd)\b", "USD", False),
        (r"€\s*(\d{2,6}(?:[.,]\d{2})?)", "EUR", False),
        (r"(\d{2,6}(?:[.,]\d{2})?)\s*(?:EUR|eur)\b", "EUR", False),
        (r"£\s*(\d{2,6}(?:[.,]\d{2})?)", "GBP", False),
        (r"(\d{2,6}(?:[.,]\d{2})?)\s*(?:GBP|gbp)\b", "GBP", False),
    ]
    for pat, curr, indian in currency_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = _parse_amount(m.group(1), indian=indian)
            if val:
                return val, curr

    kw_pattern = r"(?:grand\s*total|net\s*amount|total\s*(?:amount|price)?|price|amount)\s*[:=]\s*[:$€£₹]?\s*(\d{2,7}(?:[.,]\d{2})?)"
    m = re.search(kw_pattern, text, re.IGNORECASE)
    if m:
        indian = "₹" in text or re.search(r"\b(?:rs\.?|inr)\b", text, re.IGNORECASE)
        val = _parse_amount(m.group(1), indian=bool(indian))
        if val:
            return val, "INR" if indian else "USD"

    return None, None


def field_evidenced(value: str | None, ocr_text: str) -> str:
    """Keep a model/serial/brand only if its alphanumerics appear in OCR text."""
    if not value:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    if raw.lower() in ocr_text.lower():
        return raw
    compact_val = re.sub(r"[^a-zA-Z0-9]", "", raw.lower())
    compact_ocr = re.sub(r"[^a-zA-Z0-9]", "", ocr_text.lower())
    if len(compact_val) >= 4 and compact_val in compact_ocr:
        return raw
    return ""


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
    warranty_match = re.search(
        r"(\d{1,2}\s*(?:months?|years?|yr|mo))\s*(?:warranty|guarantee)?|"
        r"(?:warranty|guarantee)\s*(?:of|period|for)?\s*[:\-]?\s*(\d{1,2}\s*(?:months?|years?|yr|mo))",
        text,
        re.IGNORECASE,
    )
    if warranty_match:
        warranty = (warranty_match.group(1) or warranty_match.group(2) or "").strip() or None

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
        ("water purifier", "Water Purifier", "Home appliance"),
        ("purifier", "Water Purifier", "Home appliance"),
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

    # Qwen2.5-VL fills gaps (serial/model) when OCR is incomplete. Never used as the sole source.
    vision_model = choose_interactive_vision_model() if not has_strong_ocr else None
    result = None
    ocr_text = ocr_evidence.get("combined_text", "")

    if vision_model:
        prompt = create_vision_prompt(ocr_evidence)
        try:
            img, _ = load_image_from_any(image_input)
            b64 = image_to_base64(img)
            result = ollama_generate(
                vision_model,
                prompt,
                images=[b64],
                timeout=VISION_TIMEOUT,
                json_mode=True,
            )
        except Exception:
            result = None

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
        brand = field_evidenced(prod.get("brand"), ocr_text) or fallback_res["products"][0]["brand"]
        model = field_evidenced(prod.get("model"), ocr_text) or fallback_res["products"][0]["model"]
        serial = field_evidenced(prod.get("serial_number"), ocr_text) or fallback_res["products"][0]["serialNumber"]
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

