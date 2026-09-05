"""
CUSTOM YOLO MODEL TRAINING SCRIPT
Trains a high-performance custom appliance and furniture detector
using the unified 5-class dataset (AC, washing machine, closet, water purifier, cot).
Exports best weights directly to apps/ai-service/models/custom_appliances.pt.
"""

import sys
import shutil
import time
from pathlib import Path
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent
DATA_YAML = BASE_DIR / "dataset" / "data.yaml"
RUNS_DIR = BASE_DIR / "runs"
TARGET_MODEL_DIR = BASE_DIR.parent / "apps" / "ai-service" / "models"
TARGET_MODEL_PATH = TARGET_MODEL_DIR / "custom_appliances.pt"


def train_model():
    print("=" * 70)
    print("STARTING CUSTOM APPLIANCE YOLO MODEL TRAINING")
    print("=" * 70)
    print(f"Dataset Configuration: {DATA_YAML}")
    print(f"Target Output Model:   {TARGET_MODEL_PATH}")

    if not DATA_YAML.exists():
        print(f"ERROR: Dataset configuration not found at {DATA_YAML}")
        print("Please run Model/prepare_dataset.py first!")
        sys.exit(1)

    TARGET_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize Nano YOLO architecture with COCO pretrained backbone
    model = YOLO("yolov8n.pt")

    t0 = time.time()

    # Train model
    results = model.train(
        data=str(DATA_YAML.resolve()),
        epochs=25,
        imgsz=640,
        batch=16,
        device="cpu",
        workers=2,
        project=str(RUNS_DIR.resolve()),
        name="custom_appliances",
        exist_ok=True,
        verbose=True,
        patience=10,
        save=True,
        plots=True,
    )

    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print(f"TRAINING FINISHED IN {elapsed:.1f}s ({elapsed/60:.2f} mins)")
    print("=" * 70)

    # Validate model
    print("\n[VALIDATION METRICS]")
    val_metrics = model.val()
    map50 = val_metrics.box.map50
    map50_95 = val_metrics.box.map
    print(f"  -> Validation mAP@50:    {map50*100:.2f}%")
    print(f"  -> Validation mAP@50-95: {map50_95*100:.2f}%")

    # Locate best weights
    best_weights = RUNS_DIR / "custom_appliances" / "weights" / "best.pt"
    if best_weights.exists():
        shutil.copy2(best_weights, TARGET_MODEL_PATH)
        print(f"\nSuccessfully deployed best model weights to:\n  {TARGET_MODEL_PATH}")
    else:
        print(f"WARNING: Could not find best weights at {best_weights}")

    print("=" * 70)


if __name__ == "__main__":
    train_model()
