"""
MODEL EVALUATION SCRIPT
Evaluates the trained YOLO custom appliance model on the validation split
and tests live detection on sample images from each class.
"""

import sys
import json
import time
from pathlib import Path
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent
WEIGHTS_PATH = BASE_DIR.parent / "apps" / "ai-service" / "models" / "custom_appliances.pt"
DATA_YAML = BASE_DIR / "dataset" / "data.yaml"


def evaluate():
    print("=" * 75)
    print("CUSTOM APPLIANCE YOLO MODEL EVALUATION")
    print("=" * 75)
    print(f"Model Path:  {WEIGHTS_PATH}")
    print(f"Data Config: {DATA_YAML}")

    if not WEIGHTS_PATH.exists():
        print(f"ERROR: Model weights not found at {WEIGHTS_PATH}")
        sys.exit(1)

    model = YOLO(str(WEIGHTS_PATH))

    print("\nRunning Validation Set Evaluation...")
    val_results = model.val(data=str(DATA_YAML), split="val", imgsz=640, verbose=False)

    print("\n" + "=" * 75)
    print("OVERALL MODEL METRICS:")
    print("=" * 75)
    p = val_results.box.mp
    r = val_results.box.mr
    map50 = val_results.box.map50
    map50_95 = val_results.box.map

    print(f"  Precision (P):       {p * 100:.2f}%")
    print(f"  Recall (R):          {r * 100:.2f}%")
    print(f"  mAP@50:              {map50 * 100:.2f}%")
    print(f"  mAP@50-95:           {map50_95 * 100:.2f}%")

    print("\n" + "=" * 75)
    print("PER-CLASS EVALUATION BREAKDOWN:")
    print("=" * 75)
    class_names = ["AC", "Washing Machine", "Closet", "Water Purifier", "Cot"]
    
    # Class-level metrics from val_results.box
    if hasattr(val_results.box, "p") and len(val_results.box.p) > 0:
        for i, name in enumerate(class_names):
            if i < len(val_results.box.p):
                cp = val_results.box.p[i]
                cr = val_results.box.r[i]
                cmap50 = val_results.box.ap50[i]
                cmap = val_results.box.ap[i]
                print(f"  [{i}] {name:<16} | P: {cp*100:6.2f}% | R: {cr*100:6.2f}% | mAP@50: {cmap50*100:6.2f}% | mAP@50-95: {cmap*100:6.2f}%")

    # Sample live detection test across classes
    print("\n" + "=" * 75)
    print("LIVE SAMPLE INFERENCE TESTS (One sample per class):")
    print("=" * 75)

    val_images_dir = BASE_DIR / "dataset" / "images" / "val"
    val_labels_dir = BASE_DIR / "dataset" / "labels" / "val"

    tested_classes = set()
    sample_images = []

    for label_file in sorted(val_labels_dir.glob("*.txt")):
        lines = label_file.read_text().strip().splitlines()
        if not lines:
            continue
        first_cls = int(lines[0].split()[0])
        if first_cls not in tested_classes:
            tested_classes.add(first_cls)
            img_file = val_images_dir / f"{label_file.stem}.png"
            if not img_file.exists():
                img_file = val_images_dir / f"{label_file.stem}.jpg"
            if img_file.exists():
                sample_images.append((first_cls, img_file))
        if len(tested_classes) == 5:
            break

    for cls_id, img_path in sample_images:
        cls_name = class_names[cls_id]
        t0 = time.time()
        res = model.predict(source=str(img_path), imgsz=640, conf=0.25, verbose=False)
        dt = (time.time() - t0) * 1000

        detections = []
        for r in res:
            if r.boxes:
                for b in r.boxes:
                    det_id = int(b.cls[0].item())
                    det_conf = float(b.conf[0].item())
                    det_name = class_names[det_id] if det_id < len(class_names) else str(det_id)
                    detections.append(f"{det_name} ({det_conf*100:.1f}%)")

        det_str = ", ".join(detections) if detections else "No detection"
        match = "MATCH" if any(cls_name.lower() in d.lower() for d in detections) else "MISMATCH"
        print(f"  [{match}] Ground Truth: {cls_name:<16} -> Detected: {det_str:<30} ({dt:.1f}ms)")

    print("=" * 75)


if __name__ == "__main__":
    evaluate()
