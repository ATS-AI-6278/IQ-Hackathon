"""
Household Q&A: Gemma 2 answers ONLY from provided passport records.
Deterministic retrieval runs first so we never invent warranties or serials.
"""

from __future__ import annotations

from datetime import datetime, timezone
import re

from .llm import GEMMA_TIMEOUT, choose_gemma_model, ollama_generate


def parse_warranty_months(warranty: str | None) -> int | None:
    if not warranty:
        return None
    text = warranty.lower()
    years = re.search(r"(\d+)\s*(?:years?|yr)\b", text)
    if years:
        return int(years.group(1)) * 12
    months = re.search(r"(\d+)\s*(?:months?|mo)\b", text)
    if months:
        return int(months.group(1))
    digits = re.search(r"(\d{1,2})", text)
    if digits and "warranty" in text:
        value = int(digits.group(1))
        if value <= 10:
            return value * 12
        return value
    return None


def warranty_days_left(passport: dict, today: datetime | None = None) -> int | None:
    purchase = passport.get("purchaseDate")
    months = parse_warranty_months(passport.get("warranty"))
    if not purchase or not months:
        return None
    try:
        start = datetime.fromisoformat(str(purchase)[:10])
    except Exception:
        return None
    now = today or datetime.now(timezone.utc).replace(tzinfo=None)
    end_month = start.month + months
    end_year = start.year + (end_month - 1) // 12
    end_month = ((end_month - 1) % 12) + 1
    try:
        end = start.replace(year=end_year, month=end_month)
    except ValueError:
        end = start.replace(year=end_year, month=end_month, day=28)
    return (end.date() - now.date()).days


def compact_records(passports: list[dict]) -> list[dict]:
    rows = []
    for item in passports:
        days = warranty_days_left(item)
        rows.append(
            {
                "passportId": item.get("passportId"),
                "product": item.get("product"),
                "brand": item.get("brand"),
                "model": item.get("model"),
                "serialNumber": item.get("serialNumber"),
                "category": item.get("category"),
                "purchaseDate": item.get("purchaseDate"),
                "purchasePrice": item.get("purchasePrice"),
                "currency": item.get("currency"),
                "warranty": item.get("warranty"),
                "warrantyDaysLeft": days,
                "seller": item.get("seller"),
                "invoiceNumber": item.get("invoiceNumber"),
                "sourceDocument": item.get("sourceDocument"),
                "verificationStatus": item.get("verificationStatus"),
                "room": item.get("room"),
                "locationNote": item.get("locationNote"),
                "lastSeenAt": item.get("lastSeenAt"),
                "lastSeenConfidence": item.get("lastSeenConfidence"),
                "lifecycle": item.get("lifecycle"),
                "ageYears": item.get("ageYears"),
                "missing": item.get("missing") or [],
                "notes": item.get("notes"),
            }
        )
    return rows


def attention_items(records: list[dict]) -> list[dict]:
    items = []
    for row in records:
        days = row.get("warrantyDaysLeft")
        if days is not None and days <= 45:
            items.append(
                {
                    "passportId": row["passportId"],
                    "kind": "warranty",
                    "product": row["product"],
                    "detail": f"Warranty expires in {days} days" if days >= 0 else f"Warranty expired {abs(days)} days ago",
                }
            )
        name = f"{row.get('product', '')} {row.get('category', '')}".lower()
        if "purifier" in name or "filter" in name:
            items.append(
                {
                    "passportId": row["passportId"],
                    "kind": "consumable",
                    "product": row["product"],
                    "detail": "Water purifier filter typically due every 6 months — confirm last service date.",
                }
            )
        if "air conditioner" in name or row.get("product", "").lower() == "air conditioner":
            month = datetime.now().month
            if month in (3, 4, 5):
                items.append(
                    {
                        "passportId": row["passportId"],
                        "kind": "seasonal",
                        "product": row["product"],
                        "detail": "Pre-summer AC service window (filter / gas check).",
                    }
                )
    return items[:8]


def _match_records(question: str, records: list[dict]) -> list[dict]:
    q = question.lower()
    scored = []
    for row in records:
        blob = " ".join(str(v or "") for v in row.values()).lower()
        score = 0
        for token in re.findall(r"[a-z0-9]{3,}", q):
            if token in blob:
                score += 1
        aliases = {
            "ac": "air conditioner",
            "washer": "washing",
            "fridge": "refrigerator",
            "purifier": "purifier",
            "laptop": "laptop",
            "tv": "television",
        }
        for alias, target in aliases.items():
            if alias in q and target in blob:
                score += 2
        if score:
            scored.append((score, row))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in scored[:4]]


def deterministic_answer(question: str, records: list[dict]) -> dict:
    q = question.lower()
    attention = attention_items(records)
    matched = _match_records(question, records)
    focus = matched[0] if matched else None

    if any(k in q for k in ("where", "room", "located", "find the", "last seen")):
        target = focus
        if not target:
            return _refuse(question)
        room = target.get("room") or "Not placed yet"
        note = target.get("locationNote") or ""
        conf = target.get("lastSeenConfidence") or "uncertain"
        loc = f"{room}" + (f" — {note}" if note else "")
        return {
            "answer": f"{target['product']} is remembered in {loc}. Location confidence: {conf}.",
            "why": "Spatial memory from last confirmed or inferred placement — not GPS.",
            "sources": [{"passportId": target["passportId"], "field": "room", "label": target["product"]}],
            "confidence": 0.72 if conf != "confirmed" else 0.9,
            "intent": "open_passport",
            "passportId": target["passportId"],
            "engine": "deterministic",
        }

    if "kitchen" in q or "laundry" in q or "bedroom" in q or "office" in q or "living" in q:
        room_name = next((word for word in ["kitchen", "laundry", "bedroom", "office", "living"] if word in q), "")
        in_room = [row for row in records if room_name in str(row.get("room") or "").lower()]
        if any(k in q for k in ("warrant", "expir")):
            soon = [row for row in in_room if row.get("warrantyDaysLeft") is not None and row["warrantyDaysLeft"] <= 90]
            if not soon:
                return {
                    "answer": f"Nothing in {room_name} has a warranty ending in the next 90 days, from stored records.",
                    "why": "Filtered graph nodes by room, then warrantyDaysLeft.",
                    "sources": [{"passportId": row["passportId"], "field": "warranty", "label": row["product"]} for row in in_room[:4]],
                    "confidence": 0.84,
                    "intent": "attention",
                    "engine": "deterministic",
                }
            lines = "; ".join(f"{row['product']} ({row['warrantyDaysLeft']} days)" for row in soon)
            return {
                "answer": f"In {room_name}: {lines}.",
                "why": "Room filter + warranty countdown.",
                "sources": [{"passportId": row["passportId"], "field": "warranty", "label": row["product"]} for row in soon],
                "confidence": 0.88,
                "intent": "attention",
                "engine": "deterministic",
            }
        names = ", ".join(row["product"] for row in in_room) or "nothing placed"
        return {
            "answer": f"Remembered in {room_name}: {names}.",
            "why": "Household graph room assignment.",
            "sources": [{"passportId": row["passportId"], "field": "room", "label": row["product"]} for row in in_room[:5]],
            "confidence": 0.86,
            "intent": "none",
            "engine": "deterministic",
        }

    if any(k in q for k in ("how old", "years old", "age")):
        target = focus
        if not target or target.get("ageYears") is None:
            return {
                "answer": "I cannot compute age without a purchase date in the vault.",
                "why": "ageYears is derived only from purchaseDate.",
                "sources": [],
                "confidence": 0.7,
                "intent": "none",
                "engine": "deterministic",
            }
        years = float(target["ageYears"])
        return {
            "answer": f"{target['product']} is about {years:.1f} years old (from purchase date {target.get('purchaseDate')}).",
            "why": "Derived from purchaseDate. Not inferred from appearance.",
            "sources": [{"passportId": target["passportId"], "field": "purchaseDate", "label": target["product"]}],
            "confidence": 0.9,
            "intent": "open_passport",
            "passportId": target["passportId"],
            "engine": "deterministic",
        }

    if "invoice" in q or "document" in q or "receipt" in q:
        target = focus
        if not target:
            return _refuse(question)
        doc = target.get("sourceDocument")
        if not doc:
            return {
                "answer": f"There is no invoice stored for {target['product']}. I will not invent a filename.",
                "why": "sourceDocument is empty on this node.",
                "sources": [{"passportId": target["passportId"], "field": "sourceDocument", "label": target["product"]}],
                "confidence": 0.85,
                "intent": "open_passport",
                "passportId": target["passportId"],
                "engine": "deterministic",
            }
        room = target.get("room") or "unplaced"
        return {
            "answer": f"The original file remembered for {target['product']} is “{doc}”, attached to its record in {room}.",
            "why": "Document is stored as a local reference on the product node.",
            "sources": [{"passportId": target["passportId"], "field": "sourceDocument", "label": target["product"]}],
            "confidence": 0.9,
            "intent": "open_passport",
            "passportId": target["passportId"],
            "engine": "deterministic",
        }

    if "retailer" in q or "seller" in q or "bought from" in q or "store" in q:
        sellers = {}
        for row in records:
            key = (row.get("seller") or "").strip()
            if not key:
                continue
            sellers.setdefault(key, []).append(row)
        if focus and focus.get("seller"):
            return {
                "answer": f"{focus['product']} was bought from {focus['seller']}.",
                "why": "seller field on the vault node.",
                "sources": [{"passportId": focus["passportId"], "field": "seller", "label": focus["product"]}],
                "confidence": 0.9,
                "intent": "open_passport",
                "passportId": focus["passportId"],
                "engine": "deterministic",
            }
        # match seller name in question
        for seller, rows in sellers.items():
            if seller.lower() in q:
                names = ", ".join(r["product"] for r in rows)
                return {
                    "answer": f"From {seller}: {names}.",
                    "why": "Grouped graph nodes by retailer.",
                    "sources": [{"passportId": r["passportId"], "field": "seller", "label": r["product"]} for r in rows],
                    "confidence": 0.88,
                    "intent": "none",
                    "engine": "deterministic",
                }

    if any(k in q for k in ("attention", "need", "due", "expir", "health", "summary", "maintenance")):
        if not attention:
            return {
                "answer": "Nothing urgent in the household vault. All recorded warranties are more than 45 days out, and no seasonal AC window is active.",
                "why": "Computed from purchase dates and warranty durations in the local vault.",
                "sources": [{"passportId": row["passportId"], "field": "warranty", "label": row["product"]} for row in records[:3]],
                "confidence": 0.86,
                "intent": "attention",
                "engine": "deterministic",
            }
        lines = "; ".join(f"{item['product']}: {item['detail']}" for item in attention[:4])
        return {
            "answer": f"{len(attention)} item(s) need attention. {lines}",
            "why": "Warranty countdown and simple seasonal/consumable rules on your stored passports.",
            "sources": [{"passportId": item["passportId"], "field": item["kind"], "label": item["product"]} for item in attention[:4]],
            "confidence": 0.9,
            "intent": "attention",
            "engine": "deterministic",
        }

    if any(k in q for k in ("claim", "dossier", "pack")):
        target = focus or (records[0] if records else None)
        if not target:
            return _refuse(question)
        return {
            "answer": f"I can assemble a vendor claim pack for {target['product']} ({target['passportId']}) using the stored invoice fields and serial.",
            "why": "Claim packs are generated only from vault fields — no invented serials.",
            "sources": [{"passportId": target["passportId"], "field": "serialNumber", "label": target["product"]}],
            "confidence": 0.88,
            "intent": "claim_pack",
            "passportId": target["passportId"],
            "engine": "deterministic",
        }

    if "filter" in q:
        purifiers = [row for row in records if "purifier" in f"{row.get('product', '')} {row.get('category', '')}".lower()]
        if not purifiers:
            return {
                "answer": "I could not verify a water purifier or filter SKU from your uploaded passports.",
                "why": "No passport product/category contained purifier or filter.",
                "sources": [],
                "confidence": 0.7,
                "intent": "none",
                "engine": "deterministic",
            }
        row = purifiers[0]
        return {
            "answer": f"{row['product']} is in the vault (model {row.get('model') or 'not recorded'}). Compatible filter SKU is not printed on the stored invoice, so I will not invent a part number.",
            "why": "Zero-fabrication: filter SKUs only if present on a document.",
            "sources": [{"passportId": row["passportId"], "field": "model", "label": row["product"]}],
            "confidence": 0.82,
            "intent": "open_passport",
            "passportId": row["passportId"],
            "engine": "deterministic",
        }

    if any(k in q for k in ("warrant", "expire", "cover")):
        target = focus
        if not target:
            return _refuse(question)
        days = target.get("warrantyDaysLeft")
        if days is None:
            return {
                "answer": f"{target['product']} has warranty text “{target.get('warranty') or 'not recorded'}” but I cannot compute an end date without a purchase date.",
                "why": "Need both purchaseDate and warranty duration.",
                "sources": [{"passportId": target["passportId"], "field": "warranty", "label": target["product"]}],
                "confidence": 0.75,
                "intent": "open_passport",
                "passportId": target["passportId"],
                "engine": "deterministic",
            }
        status = f"{days} days remaining" if days >= 0 else f"expired {abs(days)} days ago"
        return {
            "answer": f"{target['product']} ({target['passportId']}) warranty: {target.get('warranty')}. {status}. Purchase date {target.get('purchaseDate')}.",
            "why": "End date = purchaseDate + parsed warranty duration.",
            "sources": [{"passportId": target["passportId"], "field": "purchaseDate", "label": target["product"]}],
            "confidence": 0.92,
            "intent": "warranty",
            "passportId": target["passportId"],
            "engine": "deterministic",
        }

    if any(k in q for k in ("serial", "model", "invoice", "seller", "price", "bought", "spend")):
        target = focus or (records[0] if records else None)
        if not target:
            return _refuse(question)
        return {
            "answer": (
                f"{target['product']}: brand {target.get('brand') or '—'}, model {target.get('model') or '—'}, "
                f"serial {target.get('serialNumber') or '—'}, seller {target.get('seller') or '—'}, "
                f"price {target.get('purchasePrice') or '—'} {target.get('currency') or ''}."
            ),
            "why": "Read-through of the vault record; empty fields stay empty.",
            "sources": [{"passportId": target["passportId"], "field": "serialNumber", "label": target["product"]}],
            "confidence": 0.9,
            "intent": "open_passport",
            "passportId": target["passportId"],
            "engine": "deterministic",
        }

    if focus:
        return {
            "answer": f"Closest record is {focus['product']} ({focus['passportId']}). Ask about warranty, serial, or a claim pack for a specific action.",
            "why": "Keyword overlap with vault fields.",
            "sources": [{"passportId": focus["passportId"], "field": "product", "label": focus["product"]}],
            "confidence": 0.7,
            "intent": "open_passport",
            "passportId": focus["passportId"],
            "engine": "deterministic",
        }

    return {
        "answer": "I only answer from your local household passports. Ask about a product, warranty, serial, filter, or what needs attention.",
        "why": "Question did not match a stored field.",
        "sources": [],
        "confidence": 0.6,
        "intent": "none",
        "engine": "deterministic",
    }


def _refuse(question: str) -> dict:
    return {
        "answer": "I could not verify that from your uploaded passports.",
        "why": f"No matching household record for: {question[:120]}",
        "sources": [],
        "confidence": 0.55,
        "intent": "none",
        "engine": "deterministic",
    }


def _ground_gemma(result: dict, records: list[dict], fallback: dict) -> dict:
    if not result:
        return fallback
    allowed_ids = {row.get("passportId") for row in records}
    pid = result.get("passportId")
    if pid and pid not in allowed_ids:
        result["passportId"] = fallback.get("passportId")
    answer = str(result.get("answer") or "").strip()
    if not answer:
        return fallback
    # Block obvious invention of serial-like tokens not in vault
    vault_text = " ".join(
        f"{row.get('serialNumber', '')} {row.get('model', '')} {row.get('invoiceNumber', '')}"
        for row in records
    ).lower()
    for token in re.findall(r"\b[A-Z0-9][A-Z0-9\-]{6,}\b", answer):
        if token.lower() not in vault_text.replace(" ", "") and token.lower() not in vault_text:
            return fallback
    result.setdefault("why", fallback.get("why"))
    result.setdefault("sources", fallback.get("sources") or [])
    result.setdefault("confidence", fallback.get("confidence", 0.7))
    result.setdefault("intent", fallback.get("intent", "none"))
    result["engine"] = "gemma"
    return result


def ask_household(question: str, passports: list[dict]) -> dict:
    records = compact_records(passports)
    fallback = deterministic_answer(question, records)
    model = choose_gemma_model()
    if not model or not records:
        fallback["gemmaModel"] = model
        return fallback
    if float(fallback.get("confidence") or 0) >= 0.85:
        fallback["gemmaModel"] = model
        return fallback

    prompt = f"""HOUSEHOLD_RECORDS include room, locationNote, lastSeenConfidence, ageYears, missing, seller, sourceDocument.
If location confidence is not confirmed, say so. Never invent rooms, serials, or invoices.
Return JSON only:
{{
  "answer": "plain language",
  "why": "which fields you used",
  "passportId": "id or null",
  "intent": "none" | "attention" | "warranty" | "claim_pack" | "open_passport",
  "confidence": 0.0
}}

HOUSEHOLD_RECORDS:
{records}

QUESTION: {question}
"""
    generated = ollama_generate(model, prompt, timeout=GEMMA_TIMEOUT, json_mode=True)
    grounded = _ground_gemma(generated if isinstance(generated, dict) else None, records, fallback)
    grounded["gemmaModel"] = model
    return grounded
