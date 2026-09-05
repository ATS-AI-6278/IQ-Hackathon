import requests
import base64
import json
from pathlib import Path

API_BASE = "http://127.0.0.1:5000/api"
SAMPLES = Path("samples")

def to_data_url(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = file_path.suffix.lstrip(".").lower()
    mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
    return f"data:{mime};base64,{b64}"

def test_api():
    print("Testing End-to-End API Integration...")

    # 1. Health
    h = requests.get(f"{API_BASE}/healthz").json()
    print("Health:", h)
    assert h["status"] == "ok"

    # 2. System Status
    s = requests.get(f"{API_BASE}/system/status").json()
    print("Status:", json.dumps(s, indent=2))
    assert s["backend"]["status"] == "connected"

    # 3. Product Identify (with img.jpg)
    img_path = SAMPLES / "img.jpg"
    if img_path.exists():
        print("\nTesting /product/identify with img.jpg...")
        payload = {"image": to_data_url(img_path)}
        resp = requests.post(f"{API_BASE}/product/identify", json=payload)
        print("Status code:", resp.status_code)
        det = resp.json()
        print("Identify response:", json.dumps(det, indent=2))
        assert "detectedProduct" in det
        assert "confidence" in det

        # 4. Product Match
        print("\nTesting /product/match...")
        match_resp = requests.post(f"{API_BASE}/product/match", json={"detectedProduct": det})
        print("Match response:", json.dumps(match_resp.json(), indent=2))
        assert "matches" in match_resp.json()

    # 5. Document Analysis (with image1.png)
    doc_path = SAMPLES / "image1.png"
    if doc_path.exists():
        print("\nTesting /passport/analyze-document with image1.png...")
        payload = {
            "fileName": doc_path.name,
            "fileType": "image/png",
            "content": to_data_url(doc_path)
        }
        resp = requests.post(f"{API_BASE}/passport/analyze-document", json=payload)
        print("Status code:", resp.status_code)
        analysis = resp.json()
        print("Analyze response:", json.dumps(analysis, indent=2))
        assert "documentType" in analysis
        assert len(analysis["products"]) > 0

    # 6. Passports list
    passports = requests.get(f"{API_BASE}/passports").json()
    print(f"\nPassports count: {len(passports)}")
    assert len(passports) > 0

    print("\n[OK] ALL END-TO-END INTEGRATION TESTS PASSED!")

if __name__ == "__main__":
    test_api()
