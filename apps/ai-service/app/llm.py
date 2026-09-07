"""
Local Ollama model selection.

Vision (documents + rating plates): Qwen2.5-VL
Household Q&A / triggers: Gemma 2 (2B preferred, 4B if present)
"""

from __future__ import annotations

import json
import os
import re

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
VISION_TIMEOUT = int(os.environ.get("VISION_TIMEOUT", "25"))
GEMMA_TIMEOUT = int(os.environ.get("GEMMA_TIMEOUT", "20"))
DISABLE_OLLAMA = os.environ.get("DISABLE_OLLAMA", "false").lower() in ("true", "1", "yes")

VISION_PREFS = (
    "qwen2.5vl:3b",
    "qwen2.5vl:7b",
    "qwen2.5-vl:3b",
    "qwen2.5-vl:7b",
    "qwen2.5vl",
    "qwen2.5-vl",
    "qwen3-vl",
    "llama3.2-vision",
)
GEMMA_PREFS = (
    "gemma2:2b",
    "gemma2:4b",
    "gemma2:9b",
    "gemma3:1b",
    "gemma3:4b",
    "gemma2",
    "phi3:mini",
    "phi3",
    "llama3.2:3b",
    "llama3.2:1b",
)


def list_ollama_models() -> list[str]:
    if DISABLE_OLLAMA:
        return []
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    except Exception:
        pass
    return []


def _pick(models: list[str], prefs: tuple[str, ...]) -> str | None:
    lower = {m.lower(): m for m in models}
    for pref in prefs:
        if pref in lower:
            return lower[pref]
        for name, original in lower.items():
            if pref in name:
                return original
    return None


def choose_vision_model() -> str | None:
    if os.environ.get("DISABLE_OLLAMA_VISION", "false").lower() in ("true", "1", "yes"):
        return None
    forced = os.environ.get("VISION_MODEL")
    models = list_ollama_models()
    if forced and any(forced.lower() == m.lower() for m in models):
        return next(m for m in models if m.lower() == forced.lower())
    return _pick(models, VISION_PREFS)


def vision_model_is_interactive(model: str | None) -> bool:
    """qwen3-vl:8b is installed here but does not finish a still within ~70s on CPU."""
    if not model:
        return False
    if os.environ.get("VISION_ALLOW_HEAVY", "false").lower() in ("true", "1", "yes"):
        return True
    low = model.lower()
    if "qwen3-vl" in low:
        return False
    if any(tag in low for tag in (":8b", ":7b", ":13b", ":32b", ":72b")):
        return False
    return True


def choose_interactive_vision_model() -> str | None:
    model = choose_vision_model()
    return model if vision_model_is_interactive(model) else None


def choose_gemma_model() -> str | None:
    if os.environ.get("DISABLE_OLLAMA_GEMMA", "false").lower() in ("true", "1", "yes"):
        return None
    forced = os.environ.get("GEMMA_MODEL")
    models = list_ollama_models()
    if forced and any(forced.lower() == m.lower() for m in models):
        return next(m for m in models if m.lower() == forced.lower())
    return _pick(models, GEMMA_PREFS)


def parse_json_object(text: str) -> dict | None:
    if not text:
        return None
    cleaned = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"```", "", cleaned).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        data = json.loads(cleaned[start : end + 1])
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def ollama_generate(
    model: str,
    prompt: str,
    *,
    images: list[str] | None = None,
    timeout: int = 20,
    json_mode: bool = True,
) -> dict | str | None:
    payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0},
    }
    if json_mode:
        payload["format"] = "json"
    if images:
        payload["images"] = images
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=timeout)
        if resp.status_code != 200:
            return None
        raw = resp.json().get("response", "")
        if json_mode:
            return parse_json_object(raw)
        return raw
    except Exception:
        return None
