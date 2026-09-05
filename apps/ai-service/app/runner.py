"""
CLI RUNNER BRIDGE
Allows Node.js API server to invoke AI pipelines directly via subprocess
when the FastAPI microservice is offline or when running in CLI mode.

Usage:
  python -m app.runner status
  python -m app.runner analyze <input_json_path_or_stdin>
  python -m app.runner identify <input_json_path_or_stdin>
"""

import sys
import json
from pathlib import Path

from .main import get_service_status
from .extractor import extract_products_from_image
from .detector import detect_product_from_image


def read_input(arg_val: str | None = None) -> dict:
    if arg_val and Path(arg_val).exists():
        with open(arg_val, "r", encoding="utf-8") as f:
            return json.load(f)
    elif arg_val and arg_val.strip().startswith("{"):
        return json.loads(arg_val)
    else:
        # Read from stdin
        raw = sys.stdin.read().strip()
        if raw:
            return json.loads(raw)
    return {}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided. Use: status | analyze | identify"}))
        sys.exit(1)

    cmd = sys.argv[1].lower()
    arg = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        if cmd == "status":
            res = get_service_status()
            print(json.dumps(res))
        elif cmd == "analyze":
            data = read_input(arg)
            content = data.get("content", "")
            file_name = data.get("fileName", "")
            res = extract_products_from_image(content, file_name=file_name)
            print(json.dumps(res))
        elif cmd == "identify":
            data = read_input(arg)
            image = data.get("image", "")
            res = detect_product_from_image(image)
            print(json.dumps(res))
        else:
            print(json.dumps({"error": f"Unknown command: {cmd}"}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
