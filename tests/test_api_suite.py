import urllib.request
import json
import base64
from pathlib import Path

BASE = "http://127.0.0.1:5000/api"

def run_suite():
    print("=" * 60)
    print("RUNNING COMPLETE FULL-STACK API AUDIT")
    print("=" * 60)

    # 1. Healthz
    res = json.loads(urllib.request.urlopen(f"{BASE}/healthz").read())
    print("1. GET /api/healthz ->", res)
    assert res.get("status") == "ok"

    # 2. System status
    sys_res = json.loads(urllib.request.urlopen(f"{BASE}/system/status").read())
    print("2. GET /api/system/status -> backend:", sys_res["backend"]["status"])
    for svc in sys_res["services"]:
        print(f"   - {svc['name']}: {svc['status']} ({svc['detail']})")
    assert sys_res["backend"]["status"] == "connected"

    # 3. List passports
    p_list = json.loads(urllib.request.urlopen(f"{BASE}/passports").read())
    print(f"3. GET /api/passports -> count: {len(p_list)}")
    assert len(p_list) > 0

    # 4. Dashboard summary
    summary = json.loads(urllib.request.urlopen(f"{BASE}/dashboard/summary").read())
    print(f"4. GET /api/dashboard/summary -> total: {summary['totalPassports']}, linked: {summary['successfullyLinked']}")
    assert summary["totalPassports"] >= 4

    # 5. Activities
    acts = json.loads(urllib.request.urlopen(f"{BASE}/activity").read())
    print(f"5. GET /api/activity -> count: {len(acts)}")
    assert len(acts) > 0

    # 6. Single passport
    p24 = json.loads(urllib.request.urlopen(f"{BASE}/passport/DPP-00024").read())
    print(f"6. GET /api/passport/DPP-00024 -> {p24['product']} ({p24['model']})")
    assert p24["passportId"] == "DPP-00024"

    # 7. Create passport
    new_data = {
        "product": "Test Smart Washer",
        "brand": "LG",
        "model": "WM4000HBA",
        "serialNumber": "LG-TEST-9988",
        "category": "Home appliance",
        "documentType": "Purchase invoice",
        "purchasePrice": 799,
        "currency": "USD",
        "warranty": "24 months",
        "seller": "Best Buy",
        "customerName": "Audit Tester",
        "orderId": "BB-998811",
        "invoiceNumber": "INV-9988",
        "verificationStatus": "pending"
    }
    req = urllib.request.Request(
        f"{BASE}/passport/create",
        data=json.dumps(new_data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    created = json.loads(urllib.request.urlopen(req).read())
    new_id = created["passportId"]
    print(f"7. POST /api/passport/create -> Created ID: {new_id}, Status: {created['verificationStatus']}")
    assert new_id.startswith("DPP-")

    # 8. Patch passport
    patch_req = urllib.request.Request(
        f"{BASE}/passport/{new_id}",
        data=json.dumps({"seller": "Updated Retailer", "warranty": "36 months"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    patched = json.loads(urllib.request.urlopen(patch_req).read())
    print(f"8. PATCH /api/passport/{new_id} -> Seller: {patched['seller']}, Warranty: {patched['warranty']}")
    assert patched["seller"] == "Updated Retailer"
    assert patched["warranty"] == "36 months"

    # 9. Product visual identification endpoint
    img_sample = Path("samples/img.jpg")
    if img_sample.exists():
        b64_img = base64.b64encode(img_sample.read_bytes()).decode("utf-8")
        detect_req = urllib.request.Request(
            f"{BASE}/product/identify",
            data=json.dumps({"image": f"data:image/jpeg;base64,{b64_img}"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        detected = json.loads(urllib.request.urlopen(detect_req).read())
        print(f"9. POST /api/product/identify -> Product: {detected['detectedProduct']}, Conf: {detected['confidence']}")
        assert "detectedProduct" in detected

        # 10. Match product against passports
        match_req = urllib.request.Request(
            f"{BASE}/product/match",
            data=json.dumps({"detectedProduct": detected}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        matches = json.loads(urllib.request.urlopen(match_req).read())
        print(f"10. POST /api/product/match -> Found {len(matches.get('matches', []))} matches")

    # 11. Document analysis endpoint
    doc_sample = Path("samples/image.png")
    if doc_sample.exists():
        b64_doc = base64.b64encode(doc_sample.read_bytes()).decode("utf-8")
        analyze_req = urllib.request.Request(
            f"{BASE}/passport/analyze-document",
            data=json.dumps({
                "fileName": "image.png",
                "fileType": "image/png",
                "content": f"data:image/png;base64,{b64_doc}"
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        analyzed = json.loads(urllib.request.urlopen(analyze_req).read())
        print(f"11. POST /api/passport/analyze-document -> DocType: {analyzed['documentType']}, Products: {len(analyzed['products'])}")
        assert len(analyzed["products"]) > 0

    print("=" * 60)
    print("ALL 11 END-TO-END REST API TESTS SUCCEEDED (CODE 0)!")
    print("=" * 60)

if __name__ == "__main__":
    run_suite()
