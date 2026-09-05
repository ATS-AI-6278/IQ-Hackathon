"""
DATASET PREPARATION SCRIPT
Unifies the 5 Label Studio export folders in Model/ into a standardized,
stratified train/val YOLO dataset (data.yaml).
"""

import os
import shutil
import random
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "dataset"

PROJECTS = [
    {
        "folder": "project-26-at-2026-09-04-17-38-17533b71",
        "class_id": 0,
        "name": "AC",
        "category": "Home appliance",
    },
    {
        "folder": "project-28-at-2026-09-04-17-29-de193120",
        "class_id": 1,
        "name": "washing machine",
        "category": "Home appliance",
    },
    {
        "folder": "project-29-at-2026-09-04-20-16-e89a6e86",
        "class_id": 2,
        "name": "closet",
        "category": "Furniture",
    },
    {
        "folder": "project-30-at-2026-09-04-20-52-8c184273",
        "class_id": 3,
        "name": "water purifier",
        "category": "Home appliance",
    },
    {
        "folder": "project-31-at-2026-09-04-22-14-dd5c0df3",
        "class_id": 4,
        "name": "cot",
        "category": "Furniture",
    },
]

VAL_RATIO = 0.20
RANDOM_SEED = 42


def clamp(val, min_val=0.001, max_val=0.999):
    return max(min_val, min(max_val, float(val)))


def prepare_dataset():
    random.seed(RANDOM_SEED)

    # Clean existing output directory if present
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    train_img_dir = OUTPUT_DIR / "images" / "train"
    val_img_dir = OUTPUT_DIR / "images" / "val"
    train_lbl_dir = OUTPUT_DIR / "labels" / "train"
    val_lbl_dir = OUTPUT_DIR / "labels" / "val"

    for d in [train_img_dir, val_img_dir, train_lbl_dir, val_lbl_dir]:
        d.mkdir(parents=True, exist_ok=True)

    summary = {p["name"]: {"train": 0, "val": 0} for p in PROJECTS}

    for proj in PROJECTS:
        p_dir = BASE_DIR / proj["folder"]
        img_dir = p_dir / "images"
        lbl_dir = p_dir / "labels"
        class_id = proj["class_id"]
        class_name = proj["name"]

        # Collect paired image & label files
        pairs = []
        for img_path in sorted(img_dir.glob("*.*")):
            stem = img_path.stem
            lbl_path = lbl_dir / f"{stem}.txt"
            if lbl_path.exists():
                pairs.append((img_path, lbl_path))

        # Shuffle deterministically
        random.shuffle(pairs)

        val_count = max(2, int(len(pairs) * VAL_RATIO))
        val_pairs = pairs[:val_count]
        train_pairs = pairs[val_count:]

        for img_p, lbl_p in train_pairs:
            dest_img = train_img_dir / f"{class_id}_{img_p.name}"
            dest_lbl = train_lbl_dir / f"{class_id}_{lbl_p.stem}.txt"
            shutil.copy2(img_p, dest_img)

            # Rewrite labels with mapped class_id and clamped coords
            new_lines = []
            for line in lbl_p.read_text(encoding="utf-8").splitlines():
                parts = line.strip().split()
                if len(parts) >= 5:
                    x = clamp(parts[1])
                    y = clamp(parts[2])
                    w = clamp(parts[3])
                    h = clamp(parts[4])
                    new_lines.append(f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
            dest_lbl.write_text("\n".join(new_lines), encoding="utf-8")
            summary[class_name]["train"] += 1

        for img_p, lbl_p in val_pairs:
            dest_img = val_img_dir / f"{class_id}_{img_p.name}"
            dest_lbl = val_lbl_dir / f"{class_id}_{lbl_p.stem}.txt"
            shutil.copy2(img_p, dest_img)

            # Rewrite labels with mapped class_id and clamped coords
            new_lines = []
            for line in lbl_p.read_text(encoding="utf-8").splitlines():
                parts = line.strip().split()
                if len(parts) >= 5:
                    x = clamp(parts[1])
                    y = clamp(parts[2])
                    w = clamp(parts[3])
                    h = clamp(parts[4])
                    new_lines.append(f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
            dest_lbl.write_text("\n".join(new_lines), encoding="utf-8")
            summary[class_name]["val"] += 1

    # Create data.yaml
    names_list = [p["name"] for p in PROJECTS]
    data_yaml_content = f"""# Custom Domestic Appliances Dataset
path: {OUTPUT_DIR.resolve().as_posix()}
train: images/train
val: images/val

names:
"""
    for i, name in enumerate(names_list):
        data_yaml_content += f"  {i}: {name}\n"

    yaml_path = OUTPUT_DIR / "data.yaml"
    yaml_path.write_text(data_yaml_content, encoding="utf-8")

    print("=" * 60)
    print("DATASET PREPARATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Configuration:    {yaml_path}")
    print("-" * 60)
    print(f"{'Class Name':<20} | {'Train':<8} | {'Val':<8} | {'Total':<8}")
    print("-" * 60)
    tot_train = 0
    tot_val = 0
    for name, cnts in summary.items():
        tr, vl = cnts["train"], cnts["val"]
        tot_train += tr
        tot_val += vl
        print(f"{name:<20} | {tr:<8} | {vl:<8} | {tr+vl:<8}")
    print("-" * 60)
    print(f"{'TOTAL':<20} | {tot_train:<8} | {tot_val:<8} | {tot_train+tot_val:<8}")
    print("=" * 60)


if __name__ == "__main__":
    prepare_dataset()
