import os
import sys
from PIL import Image

def create_pdfs():
    slides_dir = os.path.join(os.path.dirname(__file__), "exported_slides")
    desktop_dir = r"C:\Users\acer\Desktop\antigravity_created"
    os.makedirs(desktop_dir, exist_ok=True)

    print(f"Reading slides from: {slides_dir}")
    print(f"Output folder: {desktop_dir}")

    # Slide mapping helper
    def get_slide_img(num):
        path = os.path.join(slides_dir, f"Slide{num}.JPG")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing slide: {path}")
        im = Image.open(path)
        if im.mode != "RGB":
            im = im.convert("RGB")
        return im

    # -------------------------------------------------------------------------
    # 1. Important / Core Pitch Deck (18 Killer Slides)
    # -------------------------------------------------------------------------
    important_slide_numbers = [
        1,   # Cover: Household Intelligence OS
        2,   # Problem: Broken Ownership Lifecycle
        3,   # Shift: Paradigm Hierarchy
        4,   # Intake: Dual Commercial & Physical Anchor
        6,   # CV: Custom YOLO Appliance Detector
        7,   # ML Validation: 98.10% mAP & Confusion Matrix
        8,   # Output: Verified DPP Certificate & Seal
        9,   # Product Graph: Holographic 3D Multi-Node Model
        10,  # "Ask My House": Conversational Household Brain
        11,  # Point-and-Ask Camera Mode: Mobile AR HUD
        12,  # Attention Center: Red/Amber/Green Priority Hub
        13,  # Smart Maintenance & 1-Tap Claim Pack
        15,  # Trust & Evidence Layer: 4-Card Inspection Stack
        16,  # Phone-First: Dynamic LAN QR Bridge
        18,  # Offline & Privacy: Snapdragon NPU Edge AI
        19,  # Master Architecture: 5-Layer Stack & Bridge
        21,  # Live Demo Story: 3-Minute Walkthrough
        22   # Conclusion: We Built It. We Proved It.
    ]

    important_images = [get_slide_img(n) for n in important_slide_numbers]
    important_pdf_path = os.path.join(desktop_dir, "Verid_Household_OS_Important_Slides.pdf")
    important_images[0].save(
        important_pdf_path,
        save_all=True,
        append_images=important_images[1:],
        quality=95,
        resolution=150
    )
    print(f"[OK] Created Important Slides PDF: {important_pdf_path} ({len(important_slide_numbers)} slides)")

    # -------------------------------------------------------------------------
    # 2. Executive / Ultra-Fast Pitch Deck (Top 12 Slides)
    # -------------------------------------------------------------------------
    executive_slide_numbers = [
        1,   # Cover: Household Intelligence OS
        3,   # Shift: Paradigm Hierarchy
        4,   # Intake: Dual Anchor
        7,   # ML Validation: 98.10% mAP & Confusion Matrix
        8,   # Output: Verified DPP Certificate
        9,   # Product Graph: 12-Node Entity Model
        10,  # "Ask My House": NLP Grounded Memory
        11,  # Point-and-Ask AR Camera
        12,  # Attention Center Priority Hub
        13,  # 1-Tap Warranty Claim Pack
        18,  # Offline Snapdragon NPU Edge AI
        22   # Conclusion
    ]
    exec_images = [get_slide_img(n) for n in executive_slide_numbers]
    exec_pdf_path = os.path.join(desktop_dir, "Verid_Household_OS_Executive_Pitch_12Slides.pdf")
    exec_images[0].save(
        exec_pdf_path,
        save_all=True,
        append_images=exec_images[1:],
        quality=95,
        resolution=150
    )
    print(f"[OK] Created Executive Pitch PDF: {exec_pdf_path} ({len(executive_slide_numbers)} slides)")

    # -------------------------------------------------------------------------
    # 3. Complete Master Presentation (All 22 Slides)
    # -------------------------------------------------------------------------
    all_slide_numbers = list(range(1, 23))
    all_images = [get_slide_img(n) for n in all_slide_numbers]
    all_pdf_path = os.path.join(desktop_dir, "Verid_Household_OS_Full_Presentation_22Slides.pdf")
    all_images[0].save(
        all_pdf_path,
        save_all=True,
        append_images=all_images[1:],
        quality=95,
        resolution=150
    )
    print(f"[OK] Created Full Presentation PDF: {all_pdf_path} ({len(all_slide_numbers)} slides)")

    # Also copy the PPTX presentation into the folder for convenience
    import shutil
    pptx_source = os.path.join(os.path.dirname(__file__), "Smart_Product_Passport_Project_Presentation.pptx")
    pptx_dest = os.path.join(desktop_dir, "Smart_Product_Passport_Project_Presentation.pptx")
    shutil.copy2(pptx_source, pptx_dest)
    print(f"[OK] Copied master PPTX to: {pptx_dest}")

if __name__ == "__main__":
    create_pdfs()
