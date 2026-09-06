import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -----------------------------------------------------------------------------
# Color Constants
# -----------------------------------------------------------------------------
NAVY_DARK    = RGBColor(0x0F, 0x1B, 0x2D)  # #0F1B2D (Dark Slide Background)
NAVY_CARD    = RGBColor(0x19, 0x2B, 0x44)  # #192B44 (Dark Card Container)
NAVY_LIGHT   = RGBColor(0x23, 0x39, 0x5B)  # #23395B (Dark Accent Card)
CREAM_BG     = RGBColor(0xF7, 0xF4, 0xEC)  # #F7F4EC (Light Slide Background)
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)  # #FFFFFF (White Card Container)
GOLD         = RGBColor(0xCA, 0xA0, 0x49)  # #CAA049 (Accent Gold/Ochre)
GOLD_LIGHT   = RGBColor(0xFA, 0xF3, 0xE0)  # #FAF3E0 (Soft Gold Tint)
BLUE_ACCENT  = RGBColor(0x2A, 0x5B, 0x8C)  # #2A5B8C (Deep Slate Blue)
BLUE_LIGHT   = RGBColor(0xEE, 0xF4, 0xFB)  # #EEF4FB (Soft Blue Tint)
GREEN_TEAL   = RGBColor(0x1F, 0x7A, 0x63)  # #1F7A63 (Emerald / Teal)
GREEN_LIGHT  = RGBColor(0xEB, 0xF6, 0xF2)  # #EBF6F2 (Soft Teal Tint)
TEXT_DARK    = RGBColor(0x0F, 0x1B, 0x2D)  # Primary dark heading
TEXT_MUTED   = RGBColor(0x55, 0x65, 0x75)  # Secondary muted body
TEXT_LIGHT   = RGBColor(0xF1, 0xF5, 0xF9)  # Light text on dark cards
BORDER_LIGHT = RGBColor(0xDF, 0xD8, 0xC8)  # Subtle border for cream cards

FONT_HEADING = "Aptos"
FONT_BODY    = "Aptos"
TOTAL_SLIDES = 17

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.500)
    blank_layout = prs.slide_layouts[6]

    assets = {
        "doc": os.path.join("presentation_assets", "01_input_warranty_document.png"),
        "photo": os.path.join("presentation_assets", "02_input_physical_product_photo.png"),
        "dash": os.path.join("presentation_assets", "03_dashboard_overview.png"),
        "trust": os.path.join("presentation_assets", "04_trust_center_ai_models.png"),
        "dual": os.path.join("presentation_assets", "05_create_dual_upload_populated.png"),
        "ocr_yolo": os.path.join("presentation_assets", "06_review_ocr_and_yolo_detection.png"),
        "passport": os.path.join("presentation_assets", "07_passport_minted_verified.png"),
        "confusion": os.path.join("presentation_assets", "08_model_confusion_matrix.png"),
        "curves": os.path.join("presentation_assets", "09_model_training_metrics_curves.png"),
        "scan_match": os.path.join("presentation_assets", "10_live_scanner_match_result.png"),
        "phone_qr": os.path.join("presentation_assets", "11_phone_connect_qr_bridge.png"),
        "cert": os.path.join("presentation_assets", "12_official_dpp_certificate_seal.png"),
    }

    # Helper: Base Slide Setup
    def setup_slide(slide_num, is_dark=False):
        slide = prs.slides.add_slide(blank_layout)
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.500))
        bg.fill.solid()
        bg.fill.fore_color.rgb = NAVY_DARK if is_dark else CREAM_BG
        bg.line.fill.background()

        # Footer divider line
        divider = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(7.03), Inches(12.00), Inches(0.015))
        divider.fill.solid()
        divider.fill.fore_color.rgb = GOLD
        divider.line.fill.background()

        # Footer Left text
        tb_left = slide.shapes.add_textbox(Inches(0.65), Inches(7.06), Inches(7.50), Inches(0.25))
        tf_l = tb_left.text_frame
        tf_l.word_wrap = True
        p_l = tf_l.paragraphs[0]
        p_l.text = "Verid — Smart Digital Product Passport • iQOO Hackathon 2026"
        p_l.font.name = FONT_BODY
        p_l.font.size = Pt(9.5)
        p_l.font.color.rgb = GOLD if is_dark else TEXT_MUTED

        # Footer Right slide number
        tb_right = slide.shapes.add_textbox(Inches(11.80), Inches(7.06), Inches(0.85), Inches(0.25))
        tf_r = tb_right.text_frame
        p_r = tf_r.paragraphs[0]
        p_r.text = f"{slide_num:02d} / {TOTAL_SLIDES:02d}"
        p_r.alignment = PP_ALIGN.RIGHT
        p_r.font.name = FONT_BODY
        p_r.font.size = Pt(9.5)
        p_r.font.bold = True
        p_r.font.color.rgb = GOLD

        return slide

    # Helper: Content Header
    def add_header(slide, title, subtitle):
        tb = slide.shapes.add_textbox(Inches(0.65), Inches(0.38), Inches(12.00), Inches(0.55))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(23)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK

        tb_sub = slide.shapes.add_textbox(Inches(0.68), Inches(0.96), Inches(11.80), Inches(0.40))
        tf_sub = tb_sub.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(12.5)
        p_sub.font.color.rgb = TEXT_MUTED

    # Helper: Rounded Card
    def add_card(slide, left, top, width, height, bg_color=WHITE, border_color=BORDER_LIGHT, border_width=1):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
        return card

    # Helper: Badge / Pill
    def add_pill(slide, left, top, width, height, text, bg_color, text_color, font_size=10):
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        pill.fill.solid()
        pill.fill.fore_color.rgb = bg_color
        pill.line.fill.background()
        tf = pill.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.text = text
        p.alignment = PP_ALIGN.CENTER
        p.font.name = FONT_BODY
        p.font.size = Pt(font_size)
        p.font.bold = True
        p.font.color.rgb = text_color
        return pill

    # Helper: Image with Frame & Caption
    def add_framed_image(slide, img_path, left, top, width, height, caption=""):
        frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        frame.fill.solid()
        frame.fill.fore_color.rgb = WHITE
        frame.line.color.rgb = BORDER_LIGHT
        frame.line.width = Pt(1)

        caption_h = 0.28 if caption else 0.0
        pad = 0.06
        img_w = width - (pad * 2)
        img_h = height - (pad * 2) - caption_h

        if img_path and os.path.exists(img_path):
            slide.shapes.add_picture(img_path, Inches(left + pad), Inches(top + pad), width=Inches(img_w), height=Inches(img_h))

        if caption:
            tb = slide.shapes.add_textbox(Inches(left + pad), Inches(top + height - caption_h - 0.02), Inches(img_w), Inches(caption_h))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = caption
            p.alignment = PP_ALIGN.CENTER
            p.font.name = FONT_BODY
            p.font.size = Pt(9)
            p.font.bold = True
            p.font.color.rgb = BLUE_ACCENT

    # Helper: Bullet List Box
    def add_bullet_card(slide, left, top, width, height, title, badge_color, bullets, bold_header=None):
        card = add_card(slide, left, top, width, height, WHITE, BORDER_LIGHT, 1)
        
        # Header Badge
        add_pill(slide, left + 0.18, top + 0.18, width - 0.36, 0.35, title, badge_color, WHITE, 10.5)

        tb = slide.shapes.add_textbox(Inches(left + 0.18), Inches(top + 0.62), Inches(width - 0.36), Inches(height - 0.70))
        tf = tb.text_frame
        tf.word_wrap = True

        first = True
        if bold_header:
            p = tf.paragraphs[0]
            p.text = bold_header
            p.font.name = FONT_BODY
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = TEXT_DARK
            p.space_after = Pt(6)
            first = False

        for b in bullets:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.text = f"•  {b}"
            p.font.name = FONT_BODY
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_MUTED
            p.space_after = Pt(4)

    # =========================================================================
    # SLIDE 1: Cover Slide (Dark Theme)
    # =========================================================================
    s1 = setup_slide(1, is_dark=True)
    add_pill(s1, 0.88, 0.95, 3.40, 0.36, "iQOO HACKATHON 2026 • AI TRACK", GOLD, NAVY_DARK, 10.5)

    tb1 = s1.shapes.add_textbox(Inches(0.85), Inches(1.48), Inches(7.50), Inches(0.85))
    tf1 = tb1.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "Smart Product Passport"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(38)
    p1.font.bold = True
    p1.font.color.rgb = WHITE

    tb1_sub = s1.shapes.add_textbox(Inches(0.88), Inches(2.40), Inches(7.40), Inches(0.55))
    tf1_sub = tb1_sub.text_frame
    p1_sub = tf1_sub.paragraphs[0]
    p1_sub.text = "Verid: Transforming Scattered Household Evidence into Living Digital Identity"
    p1_sub.font.name = FONT_BODY
    p1_sub.font.size = Pt(16)
    p1_sub.font.color.rgb = RGBColor(0xD2, 0xDC, 0xE6)

    tb1_desc = s1.shapes.add_textbox(Inches(0.88), Inches(3.08), Inches(7.20), Inches(0.85))
    tf1_desc = tb1_desc.text_frame
    tf1_desc.word_wrap = True
    p1_desc = tf1_desc.paragraphs[0]
    p1_desc.text = "Commercial Evidence (Invoice / Warranty Card) + Physical Hardware Proof (Appliance Photo) → Computer Vision & RapidOCR Verification → Living Digital Product Passport & Private AI House Memory"
    p1_desc.font.name = FONT_BODY
    p1_desc.font.size = Pt(12.5)
    p1_desc.font.color.rgb = GOLD

    badges_s1 = [
        ("Custom YOLOv8 (98.1% mAP)", BLUE_ACCENT),
        ("RapidOCR Zero-Fabrication", GREEN_TEAL),
        ("Bounded Qwen3-VL 8B", BLUE_ACCENT),
        ("Private AI House Memory", GOLD),
    ]
    bx = 0.88
    for text, color in badges_s1:
        add_pill(s1, bx, 4.15, 1.72, 0.32, text, color, WHITE, 8.5)
        bx += 1.80

    # Right Card: Digital Passport Emblem
    add_card(s1, 8.65, 1.15, 3.85, 5.00, NAVY_CARD, GOLD, border_width=2)
    tb_emb = s1.shapes.add_textbox(Inches(8.95), Inches(1.40), Inches(3.25), Inches(0.40))
    p_emb = tb_emb.text_frame.paragraphs[0]
    p_emb.text = "VERID DPP REGISTRY"
    p_emb.font.bold = True
    p_emb.font.size = Pt(13)
    p_emb.font.color.rgb = GOLD

    tb_emb_t = s1.shapes.add_textbox(Inches(8.95), Inches(1.90), Inches(3.25), Inches(2.10))
    tf_emb_t = tb_emb_t.text_frame
    tf_emb_t.word_wrap = True
    lines = [
        "Product: Electrolux EcoCare 900",
        "Category: Washing Machine (YOLO)",
        "Serial: SN-WM900-2026-8842",
        "Warranty: 2 Years (Active)",
        "Repair Index: 8.6 / 10 · Class A++",
        "Deterministic Hash: 0x4d50502d...",
        "Anchor: Hardware Photo Linked",
    ]
    for i, line in enumerate(lines):
        p = tf_emb_t.paragraphs[0] if i == 0 else tf_emb_t.add_paragraph()
        p.text = line
        p.font.size = Pt(10)
        p.font.color.rgb = WHITE if i == 0 else RGBColor(0xCB, 0xD5, 0xE1)

    add_pill(s1, 8.95, 4.15, 3.25, 0.34, "✓ PHYSICALLY VERIFIED BY YOLO", GREEN_TEAL, WHITE, 9)
    add_pill(s1, 8.95, 4.58, 3.25, 0.34, "📱 PHONE SCANNER CONNECTED", BLUE_ACCENT, WHITE, 9)
    add_pill(s1, 8.95, 5.00, 3.25, 0.34, "EU ECODESIGN DPP COMPLIANT", GOLD, NAVY_DARK, 9)

    tb1_bot = s1.shapes.add_textbox(Inches(0.88), Inches(6.15), Inches(7.50), Inches(0.50))
    p1_b = tb1_bot.text_frame.paragraphs[0]
    p1_b.text = "AI-Powered Product Identity • Real Hardware Anchoring • Warranty Shield • Bill Intelligence"
    p1_b.font.size = Pt(12)
    p1_b.font.bold = True
    p1_b.font.color.rgb = RGBColor(0xDF, 0xE7, 0xEF)

    # =========================================================================
    # SLIDE 2: The Problem (Preserved Structure + Enhanced Clarity)
    # =========================================================================
    s2 = setup_slide(2)
    add_header(s2, "The Problem: Broken Ownership Lifecycle", "Why household asset management and warranty tracking fails in every home today")

    add_bullet_card(s2, 0.70, 1.65, 3.75, 4.10, "01  INFORMATION IS LOST", BLUE_ACCENT, [
        "Model and serial numbers fade or hide behind heavy appliances.",
        "Paper receipts, bills, and warranty cards sit forgotten in random drawers.",
        "Warranty terms and conditions remain buried inside unread manuals.",
        "Users spend hours searching through old paperwork during unexpected breakdowns.",
    ], "Product information is scattered across detached physical sources.")

    add_bullet_card(s2, 4.80, 1.65, 3.75, 4.10, "02  WARRANTY IS MISSED", GOLD, [
        "Over 80% of consumer warranties lapse unnoticed without owner reminders.",
        "Misplaced purchase receipts make official claims impossible with vendors.",
        "Coverage expirations are discovered only after paying for avoidable repairs.",
        "Zero centralized visibility exists across all household products.",
    ], "Owning an appliance does not mean actively managing its warranty.")

    add_bullet_card(s2, 8.90, 1.65, 3.75, 4.10, "03  BILLS & COSTS ARE OPAQUE", GREEN_TEAL, [
        "Bills pack multiple hidden charges, taxes, and peak tariffs.",
        "Sudden monthly spikes (e.g. +31%) lack clear appliance attribution.",
        "Late penalty fees and billing anomalies slip through unnoticed.",
        "No intelligent system connects physical appliances to running costs.",
    ], "A utility bill shows how much was paid, but never why it jumped.")

    # Bottom Takeaway Card
    bot_card = add_card(s2, 0.70, 6.00, 11.95, 0.65, WHITE, GOLD, 1.5)
    tb_b = s2.shapes.add_textbox(Inches(0.85), Inches(6.08), Inches(11.65), Inches(0.50))
    p_b = tb_b.text_frame.paragraphs[0]
    p_b.text = "The problem is not a lack of documents — it is the lack of an intelligent system that anchors, connects, and explains them."
    p_b.font.size = Pt(12)
    p_b.font.bold = True
    p_b.font.color.rgb = TEXT_DARK
    p_b.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 3: Our Solution (Dual-Evidence Core Formula + Workflow)
    # =========================================================================
    s3 = setup_slide(3)
    add_header(s3, "Our Solution: The Verid Platform", "Turning real-world evidence into verified, living digital product passports")

    # Formula Box
    formula_card = add_card(s3, 0.70, 1.55, 11.95, 0.85, NAVY_DARK, GOLD, 1.5)
    tb_form = s3.shapes.add_textbox(Inches(0.85), Inches(1.62), Inches(11.65), Inches(0.70))
    tf_form = tb_form.text_frame
    p_f1 = tf_form.paragraphs[0]
    p_f1.text = "[ Commercial Evidence: Invoice / Warranty PDF ]  +  [ Physical Evidence: Hardware Appliance Photo ]"
    p_f1.font.size = Pt(13)
    p_f1.font.bold = True
    p_f1.font.color.rgb = GOLD
    p_f1.alignment = PP_ALIGN.CENTER

    p_f2 = tf_form.add_paragraph()
    p_f2.text = "↳ Verified by Computer Vision & RapidOCR  →  [ Living Digital Product Passport ]"
    p_f2.font.size = Pt(12)
    p_f2.font.color.rgb = WHITE
    p_f2.alignment = PP_ALIGN.CENTER

    # 6 Step Workflow Cards
    steps = [
        ("SCAN PRODUCT", "Mobile camera identifies physical appliance via YOLO", BLUE_ACCENT),
        ("CREATE PASSPORT", "Digital identity minted with permanent evidence links", GOLD),
        ("SCAN EVIDENCE", "RapidOCR extracts serial, date, warranty, and seller", GREEN_TEAL),
        ("WARRANTY SHIELD", "Automated countdown alerts before coverage lapses", BLUE_ACCENT),
        ("AI ASSISTANT", "Zero-hallucination chat grounded in source documents", GOLD),
        ("ANALYSE BILLS", "Explains why monthly utility and repair costs changed", GREEN_TEAL),
    ]
    sw = 1.88
    sgap = 0.13
    sx = 0.70
    for i, (title, desc, color) in enumerate(steps):
        add_card(s3, sx, 2.65, sw, 2.70, WHITE, BORDER_LIGHT, 1)
        add_pill(s3, sx + 0.10, 2.75, sw - 0.20, 0.32, title, color, WHITE, 8.5)
        
        tb_s = s3.shapes.add_textbox(Inches(sx + 0.12), Inches(3.20), Inches(sw - 0.24), Inches(1.95))
        tf_s = tb_s.text_frame
        tf_s.word_wrap = True
        p_s = tf_s.paragraphs[0]
        p_s.text = desc
        p_s.font.size = Pt(10)
        p_s.font.color.rgb = TEXT_MUTED

        if i < len(steps) - 1:
            ch = s3.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(sx + sw + 0.02), Inches(3.85), Inches(0.09), Inches(0.25))
            ch.fill.solid()
            ch.fill.fore_color.rgb = GOLD
            ch.line.fill.background()

        sx += sw + sgap

    # Bottom Explanation
    add_card(s3, 0.70, 5.55, 11.95, 1.15, WHITE, BORDER_LIGHT, 1)
    tb_sol_b = s3.shapes.add_textbox(Inches(0.90), Inches(5.65), Inches(11.55), Inches(0.95))
    tf_sb = tb_sol_b.text_frame
    tf_sb.word_wrap = True
    p_sb1 = tf_sb.paragraphs[0]
    p_sb1.text = "A physical product becomes a persistent, cryptographically sealed digital record."
    p_sb1.font.bold = True
    p_sb1.font.size = Pt(12)
    p_sb1.font.color.rgb = TEXT_DARK

    p_sb2 = tf_sb.add_paragraph()
    p_sb2.text = "Original photos and documents remain permanently anchored as verifiable evidence; AI extracts structured parameters, predicts maintenance needs, and answers queries with zero fabrication."
    p_sb2.font.size = Pt(10.5)
    p_sb2.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: Real Intake: Commercial & Physical Evidence (Dual Upload)
    # =========================================================================
    s4 = setup_slide(4)
    add_header(s4, "1. Dual-Evidence Intake: Paper + Physical Proof", "Real inputs captured together to anchor product identity without manual typing")

    # Left Column: Commercial Document
    add_card(s4, 0.70, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s4, 0.90, 1.80, 5.40, 0.35, "COMMERCIAL ANCHOR (INVOICE / RECEIPT)", BLUE_ACCENT, WHITE, 10.5)
    add_framed_image(s4, assets["doc"], 0.90, 2.30, 5.40, 2.50, "Electrolux EcoCare 900 Warranty Document (PDF / Image)")
    
    tb_doc = s4.shapes.add_textbox(Inches(0.90), Inches(4.95), Inches(5.40), Inches(1.55))
    tf_doc = tb_doc.text_frame
    tf_doc.word_wrap = True
    doc_bullets = [
        "Captures legal commercial transaction: Seller, Customer, Date, Price.",
        "Contains manufacturer model code, order ID, and official warranty terms.",
        "RapidOCR extracts structured fields automatically without tedious manual typing.",
    ]
    for i, b in enumerate(doc_bullets):
        p = tf_doc.paragraphs[0] if i == 0 else tf_doc.add_paragraph()
        p.text = f"• {b}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # Right Column: Physical Hardware Photo
    add_card(s4, 6.85, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s4, 7.05, 1.80, 5.40, 0.35, "HARDWARE ANCHOR (REAL APPLIANCE PHOTO)", GREEN_TEAL, WHITE, 10.5)
    add_framed_image(s4, assets["photo"], 7.95, 2.30, 3.60, 2.50, "Physical Appliance Photo (Captured on Phone Camera)")

    tb_pho = s4.shapes.add_textbox(Inches(7.05), Inches(4.95), Inches(5.40), Inches(1.55))
    tf_pho = tb_pho.text_frame
    tf_pho.word_wrap = True
    pho_bullets = [
        "Proves physical possession in the room, stopping paper-only return fraud.",
        "Custom YOLO identifies product class (Washing Machine) & computes match score.",
        "⚡ 1-Click Demo Presets included for instant hackathon evaluation.",
    ]
    for i, b in enumerate(pho_bullets):
        p = tf_pho.paragraphs[0] if i == 0 else tf_pho.add_paragraph()
        p.text = f"• {b}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5: Document AI: RapidOCR & Semantic Extraction
    # =========================================================================
    s5 = setup_slide(5)
    add_header(s5, "2. Document AI: RapidOCR & Semantic Extraction", "Sub-150ms offline text extraction with zero-hallucination semantic parsing")

    # Left Column: Screenshot of Populated Form
    add_framed_image(s5, assets["ocr_yolo"], 0.70, 1.65, 6.60, 5.00, "Reviewing Extracted Document Metadata & YOLO Detection Signals")

    # Right Column: Technical Details Card
    add_card(s5, 7.50, 1.65, 5.15, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s5, 7.70, 1.82, 4.75, 0.35, "EXTRACTION ENGINE & ZERO-HALLUCINATION PARSING", BLUE_ACCENT, WHITE, 10)

    tb_pipe = s5.shapes.add_textbox(Inches(7.70), Inches(2.30), Inches(4.75), Inches(4.20))
    tf_pipe = tb_pipe.text_frame
    tf_pipe.word_wrap = True

    pipe_points = [
        ("⚡ RapidOCR Engine", "High-speed offline ONNX inference (~120ms); extracts raw text lines with high resilience against crumpled receipts and phone camera angles."),
        ("🛡️ Zero-Fabrication Parser", "Applies strict regex matching against certified model patterns and serial numbers; never uses generative text guessing for critical identifiers."),
        ("📋 Extracted Entity Schema", "• Product: Electrolux EcoCare 900\n• Model: EWF9042R7WB  • Category: Washing Machine\n• Serial: SN-WM900-2026-8842\n• Purchase Date: 12 Aug 2026  • Price: $1,299 USD\n• Warranty: 2 Years Official Manufacturer Coverage"),
        ("✓ Human-in-the-Loop Review", "Extracted fields are presented clearly for 1-tap confirmation or edit before permanent cryptographic passport minting."),
    ]
    for i, (hd, body) in enumerate(pipe_points):
        p = tf_pipe.paragraphs[0] if i == 0 else tf_pipe.add_paragraph()
        p.text = hd
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(2)

        pb = tf_pipe.add_paragraph()
        pb.text = body
        pb.font.size = Pt(9.5)
        pb.font.color.rgb = TEXT_MUTED
        pb.space_after = Pt(6)

    # =========================================================================
    # SLIDE 6: Computer Vision: Fine-Tuned Custom YOLO Appliance Detector
    # =========================================================================
    s6 = setup_slide(6)
    add_header(s6, "3. Computer Vision: Custom YOLO Appliance Detector", "Fine-tuned object localization with bounding-box confidence verification")

    add_framed_image(s6, assets["dual"], 0.70, 1.65, 6.60, 5.00, "1-Click Dual Intake: Visual Hardware Anchor & Document Upload")

    # Right Card: Computer Vision Engineering
    add_card(s6, 7.50, 1.65, 5.15, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s6, 7.70, 1.82, 4.75, 0.35, "APPLIANCE VISION ARCHITECTURE", GREEN_TEAL, WHITE, 10)

    tb_cv = s6.shapes.add_textbox(Inches(7.70), Inches(2.30), Inches(4.75), Inches(4.20))
    tf_cv = tb_cv.text_frame
    tf_cv.word_wrap = True

    cv_points = [
        ("🎯 Custom Fine-Tuned YOLOv8", "Trained specifically on household appliance domains for sub-100ms CPU inference; produces tight bounding boxes and classification scores."),
        ("🏷️ 5 Core Appliance Classes", "1. Washing Machine    2. Air Conditioner (AC)\n3. Closet / Wardrobe   4. Water Purifier\n5. Cot / Bed"),
        ("📦 Multi-Object Isolation", "Detects multiple appliances in cluttered rooms independently; creates separated passports rather than collapsing the entire room into one record."),
        ("🔄 Multi-Model Fallback Hierarchy", "• Tier 1: Custom YOLO Appliance Core (~80ms)\n• Tier 2: COCO Foundation Detector fallback (~90ms)\n• Tier 3: Bounded Qwen3-VL 8B vision fallback (~1.2s)"),
    ]
    for i, (hd, body) in enumerate(cv_points):
        p = tf_cv.paragraphs[0] if i == 0 else tf_cv.add_paragraph()
        p.text = hd
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(2)

        pb = tf_cv.add_paragraph()
        pb.text = body
        pb.font.size = Pt(9.5)
        pb.font.color.rgb = TEXT_MUTED
        pb.space_after = Pt(6)

    # =========================================================================
    # SLIDE 7: AI/ML Validation Performance (15% Technical Depth)
    # =========================================================================
    s7 = setup_slide(7)
    add_header(s7, "4. AI/ML Validation: Proven Empirical Results", "Empirically measured validation performance on custom household appliance dataset")

    # Metrics 4-Box Grid
    metrics = [
        ("98.10%", "mAP@50", "Appliance localization accuracy", BLUE_ACCENT),
        ("99.29%", "Precision", "Near-zero false positive alarms", GREEN_TEAL),
        ("98.57%", "Recall", "Detects appliances in clutter", GOLD),
        ("~69-96 ms", "CPU Latency", "Instant edge execution speed", BLUE_ACCENT),
    ]
    mw = 2.85
    mgap = 0.18
    mx = 0.70
    for val, label, sub, color in metrics:
        add_card(s7, mx, 1.65, mw, 1.15, WHITE, BORDER_LIGHT, 1)
        tb_m = s7.shapes.add_textbox(Inches(mx + 0.10), Inches(1.70), Inches(mw - 0.20), Inches(1.05))
        tf_m = tb_m.text_frame
        tf_m.word_wrap = True
        p_val = tf_m.paragraphs[0]
        p_val.text = val
        p_val.font.name = FONT_HEADING
        p_val.font.size = Pt(20)
        p_val.font.bold = True
        p_val.font.color.rgb = color
        p_val.alignment = PP_ALIGN.CENTER

        p_lbl = tf_m.add_paragraph()
        p_lbl.text = f"{label} • {sub}"
        p_lbl.font.size = Pt(8.5)
        p_lbl.font.color.rgb = TEXT_MUTED
        p_lbl.alignment = PP_ALIGN.CENTER

        mx += mw + mgap

    # Two Charts Side by Side
    add_framed_image(s7, assets["confusion"], 0.70, 2.95, 5.80, 3.65, "Normalized Confusion Matrix: 99%+ Diagonal Accuracy Across 5 Classes")
    add_framed_image(s7, assets["curves"], 6.85, 2.95, 5.80, 3.65, "Loss Convergence & mAP Curves Across 15 Epochs on Custom Appliance Dataset")

    # =========================================================================
    # SLIDE 8: The Verified Digital Product Passport (Output Phase)
    # =========================================================================
    s8 = setup_slide(8)
    add_header(s8, "5. The Output: Verified Digital Product Passport", "An immutable, standards-compliant digital asset anchored to physical proof")

    # Left: Passport Minted Detail
    add_framed_image(s8, assets["passport"], 0.70, 1.65, 5.80, 3.60, "Verified Passport Record: Verification Posture & Commercial Evidence")
    
    tb_p_notes = s8.shapes.add_textbox(Inches(0.70), Inches(5.35), Inches(5.80), Inches(1.30))
    tf_pn = tb_p_notes.text_frame
    tf_pn.word_wrap = True
    pn_points = [
        "Hardware Anchor Proof: Real appliance photo bound permanently to record.",
        "Sub-200ms Search: Instant registry lookup by Serial, Model, Brand, or QR ID.",
        "Audit Trail: Complete chronological timeline of minting, edits, and checks.",
    ]
    for i, pt in enumerate(pn_points):
        p = tf_pn.paragraphs[0] if i == 0 else tf_pn.add_paragraph()
        p.text = f"✓ {pt}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # Right: Official DPP Certificate
    add_framed_image(s8, assets["cert"], 6.85, 1.65, 5.80, 3.60, "Official Verid DPP Certificate: EU Ecodesign Seal, QR & Cryptographic Hash")

    tb_c_notes = s8.shapes.add_textbox(Inches(6.85), Inches(5.35), Inches(5.80), Inches(1.30))
    tf_cn = tb_c_notes.text_frame
    tf_cn.word_wrap = True
    cn_points = [
        "Cryptographic SHA-256 Seal: Unique deterministic hash sealing invoice + photo.",
        "EU Ecodesign Compliant: Repairability Index (8.6/10) and Eco Class (A++).",
        "1-Click Print & PDF Export: Ready for warranty claim filing and resale transfer.",
    ]
    for i, pt in enumerate(cn_points):
        p = tf_cn.paragraphs[0] if i == 0 else tf_cn.add_paragraph()
        p.text = f"✓ {pt}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 9: Lifecycle Intelligence: Proactive Guardian
    # =========================================================================
    s9 = setup_slide(9)
    add_header(s9, "6. Lifecycle Intelligence: Proactive Guardian", "Active monitoring that turns passive documents into automated home protection")

    # Top Dashboard View
    add_framed_image(s9, assets["dash"], 0.70, 1.65, 11.95, 2.75, "Live Overview Dashboard with Smart Guardian & Circular Economy Pulse")

    # Bottom 3 Cards
    add_bullet_card(s9, 0.70, 4.55, 3.80, 2.10, "WARRANTY SHIELD (100% ACTIVE)", GREEN_TEAL, [
        "Active monitoring across all registered household appliances.",
        "Automated countdown alerts triggered at 90, 60, and 30-day windows.",
        "Eliminates missed deadlines and out-of-pocket repair costs.",
    ], "Zero Expired Household Assets")

    add_bullet_card(s9, 4.77, 4.55, 3.80, 2.10, "PREDICTIVE MAINTENANCE AI", GOLD, [
        "Schedules preventive maintenance based on appliance category.",
        "Electrolux Washer: 30-day drum descaling & lint flush alert.",
        "Haier Inverter AC: Pre-season antimicrobial filter cleaning reminder.",
    ], "Filter & Service Recommendations")

    add_bullet_card(s9, 8.85, 4.55, 3.80, 2.10, "CIRCULAR ECODESIGN (94.8%)", BLUE_ACCENT, [
        "Aligns with European Digital Product Passport directives.",
        "Tracks repairability index, component lineage, and materials.",
        "Substantially increases secondary resale value through proof.",
    ], "Circular Economy Ready")

    # =========================================================================
    # SLIDE 10: Phone-First Experience: Instant Mobile QR Bridge (15% Rubric)
    # =========================================================================
    s10 = setup_slide(10)
    add_header(s10, "7. Phone-First Experience: Instant Mobile QR Bridge", "Turning any smartphone into an enterprise hardware scanner with zero app installation")

    # Left: Phone QR Modal
    add_framed_image(s10, assets["phone_qr"], 0.70, 1.65, 5.80, 3.45, "Dynamic QR Bridge: Instant Local LAN Connection for iQOO / Android Phones")

    tb_qr_t = s10.shapes.add_textbox(Inches(0.70), Inches(5.25), Inches(5.80), Inches(1.40))
    tf_qt = tb_qr_t.text_frame
    tf_qt.word_wrap = True
    qr_points = [
        "Dynamic LAN QR Pairing: Direct connection to http://192.168.1.4:5173/scan.",
        "Zero-Install Convenience: Judges simply scan with phone camera to launch live scanner.",
        "No App Store download or configuration required; runs immediately in browser.",
    ]
    for i, pt in enumerate(qr_points):
        p = tf_qt.paragraphs[0] if i == 0 else tf_qt.add_paragraph()
        p.text = f"📱 {pt}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # Right: Live Scanner Match
    add_framed_image(s10, assets["scan_match"], 6.85, 1.65, 5.80, 3.45, "Live Mobile Scanner: Sub-200ms Recognition & Passport Matching")

    tb_sm_t = s10.shapes.add_textbox(Inches(6.85), Inches(5.25), Inches(5.80), Inches(1.40))
    tf_st = tb_sm_t.text_frame
    tf_st.word_wrap = True
    sm_points = [
        "Sub-200ms Match Speed: Point phone at appliance → YOLO detects → match found.",
        "Dual Operational Synergy: Mobile handset is the capture tool; PC is the registry.",
        "Essential Phone Role: Makes the smartphone an active scanner in daily home life.",
    ]
    for i, pt in enumerate(sm_points):
        p = tf_st.paragraphs[0] if i == 0 else tf_st.add_paragraph()
        p.text = f"⚡ {pt}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 11: AI Product Assistant & Document Grounding
    # =========================================================================
    s11 = setup_slide(11)
    add_header(s11, "8. AI Assistant: Evidence-Grounded Conversation", "Natural language queries answered strictly from verified passport and document evidence")

    add_bullet_card(s11, 0.70, 1.65, 5.80, 5.00, "NATURAL LANGUAGE INQUIRIES", BLUE_ACCENT, [
        "“What is the warranty status of my Electrolux washing machine?”",
        "“Is motor replacement covered under the primary warranty terms?”",
        "“Show me the original purchase invoice and model number.”",
        "“Which appliances in my house need maintenance this month?”",
        "“What was the purchase date and price of my living room AC?”",
        "“Generate an official claim email with serial number and invoice attached.”",
    ], "Direct Questions Across Household Possessions")

    add_bullet_card(s11, 6.85, 1.65, 5.80, 5.00, "STRICT EVIDENCE GROUNDING ARCHITECTURE", GREEN_TEAL, [
        "Zero-Hallucination Retrieval: Answers derived strictly from indexed passport fields and OCR text blocks.",
        "Exact Source Document Citation: AI cites the specific line item, date, and vendor from original invoice.",
        "Proactive Lifecycle Advisory: Suggests official customer service helplines and claim requirements.",
        "Unified Household Search: Aggregates across electronics, appliances, and furniture in one chat.",
        "Privacy Preserving: Sensitive receipt details remain within local registry storage.",
    ], "Trust Through Verifiable Provenance")

    # =========================================================================
    # SLIDE 12: Bill Intelligence: "Why Is My Bill So High?"
    # =========================================================================
    s12 = setup_slide(12)
    add_header(s12, "9. Bill Intelligence: Transparent Cost Explanations", "Deconstructing utility and service bills into plain-language financial insights")

    # Left Card: Breakdown
    add_card(s12, 0.70, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s12, 0.90, 1.82, 5.40, 0.35, "₹4,872 ELECTRICITY BILL BREAKDOWN", BLUE_ACCENT, WHITE, 10.5)

    tb_bill_t = s12.shapes.add_textbox(Inches(0.90), Inches(2.35), Inches(5.40), Inches(4.10))
    tf_bt = tb_bill_t.text_frame
    tf_bt.word_wrap = True

    bill_items = [
        ("Base Charge", "₹2,100", "Standard fixed connection fee"),
        ("Usage Energy Charge", "₹1,730", "Summer AC peak kilowatt consumption"),
        ("Electricity Duty & Tax", "₹420", "Government utility tax tariff"),
        ("Late Payment Surcharge", "₹300", "Avoidable late fee penalty"),
        ("Other Adjustments", "₹322", "Regulatory surcharge"),
    ]
    for item, cost, sub in bill_items:
        p = tf_bt.add_paragraph() if tf_bt.paragraphs[0].text else tf_bt.paragraphs[0]
        p.text = f"{item.ljust(25)} {cost}"
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_DARK
        
        ps = tf_bt.add_paragraph()
        ps.text = f"   ↳ {sub}"
        ps.font.size = Pt(9)
        ps.font.color.rgb = TEXT_MUTED
        ps.space_after = Pt(4)

    p_div = tf_bt.add_paragraph()
    p_div.text = "Last Month: ₹3,714   →   Current Month: ₹4,872   (+31% Net Increase)"
    p_div.font.bold = True
    p_div.font.size = Pt(10.5)
    p_div.font.color.rgb = RGBColor(0xB9, 0x1C, 0x1C)

    # Right Card: Plain-Language Explanation
    add_card(s12, 6.85, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s12, 7.05, 1.82, 5.40, 0.35, "AI PLAIN-LANGUAGE EXPLANATION", GOLD, NAVY_DARK, 10.5)

    # Quote Box
    q_box = add_card(s12, 7.05, 2.35, 5.40, 1.30, GOLD_LIGHT, GOLD, 1.5)
    tb_q = s12.shapes.add_textbox(Inches(7.20), Inches(2.45), Inches(5.10), Inches(1.10))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    p_q = tf_q.paragraphs[0]
    p_q.text = "“Your bill increased 31% primarily due to higher seasonal AC usage (+₹1,730) and an avoidable ₹300 late fee.”"
    p_q.font.size = Pt(12)
    p_q.font.bold = True
    p_q.font.color.rgb = TEXT_DARK

    tb_b_exp = s12.shapes.add_textbox(Inches(7.05), Inches(3.80), Inches(5.40), Inches(2.70))
    tf_be = tb_b_exp.text_frame
    tf_be.word_wrap = True
    b_points = [
        ("Appliance Attribution", "Connects electricity surge directly to high-draw appliances identified in passports (e.g. Inverter AC vs Refrigerator)."),
        ("Tariff & Penalty Detection", "Flags hidden penalty fees and tariff changes that are typically buried in complex fine print."),
        ("Actionable Cost Prevention", "Automates bill payment reminders and advises eco-cooling modes to prevent future late fees."),
    ]
    for hd, txt in b_points:
        p = tf_be.add_paragraph() if tf_be.paragraphs[0].text else tf_be.paragraphs[0]
        p.text = f"• {hd}:"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_DARK
        
        pt = tf_be.add_paragraph()
        pt.text = f"  {txt}"
        pt.font.size = Pt(9.5)
        pt.font.color.rgb = TEXT_MUTED
        pt.space_after = Pt(4)

    # =========================================================================
    # SLIDE 13: Technical Architecture: Specialized AI Pipeline
    # =========================================================================
    s13 = setup_slide(13)
    add_header(s13, "10. Technical Architecture: Specialized AI Pipeline", "Coordinated microservices combining edge vision, OCR, and local language models")

    # 4 Architecture Columns
    arch_cols = [
        ("1. CLIENT TIER", BLUE_ACCENT, [
            "Vite 7 + React 19 + TypeScript",
            "Tailwind CSS + Lucide Icons",
            "HTML5 Camera Scanner",
            "Dynamic QR LAN Bridge (192.168.1.4:5173)",
            "Responsive Desktop & Mobile UI",
        ], "Web UI & Mobile Scanner"),

        ("2. API GATEWAY", GOLD, [
            "Node.js Express + TypeScript",
            "Zod Runtime Schema Validation",
            "Multi-Factor Matching Engine",
            "SHA-256 Cryptographic Hasher",
            "SQLite Document Database",
        ], "Gateway & Passport Vault"),

        ("3. AI CORE ENGINE", GREEN_TEAL, [
            "Python FastAPI Microservice",
            "Custom YOLOv8 Appliance (~80ms)",
            "RapidOCR Offline Engine (~120ms)",
            "COCO Foundation Detector Fallback",
            "Qwen3-VL 8B (Ollama Local)",
        ], "Vision & Document AI"),

        ("4. VERIFIED PASSPORT", BLUE_ACCENT, [
            "Immutable Audit Timeline",
            "Hardware Photo Anchor Proof",
            "EU Ecodesign DPP Compliance",
            "Repairability Index (8.6/10)",
            "1-Click PDF / Print Certificate",
        ], "Living Digital Identity"),
    ]
    aw = 2.85
    agap = 0.18
    ax = 0.70
    for title, color, points, sub in arch_cols:
        add_card(s13, ax, 1.65, aw, 5.00, WHITE, BORDER_LIGHT, 1)
        add_pill(s13, ax + 0.15, 1.82, aw - 0.30, 0.35, title, color, WHITE, 10)

        tb_a = s13.shapes.add_textbox(Inches(ax + 0.15), Inches(2.28), Inches(aw - 0.30), Inches(4.20))
        tf_a = tb_a.text_frame
        tf_a.word_wrap = True

        p_sub = tf_a.paragraphs[0]
        p_sub.text = sub
        p_sub.font.bold = True
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_DARK
        p_sub.space_after = Pt(8)

        for pt in points:
            p = tf_a.add_paragraph()
            p.text = f"• {pt}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_MUTED
            p.space_after = Pt(4)

        ax += aw + agap

    # =========================================================================
    # SLIDE 14: Why We Are Different: Traditional Storage vs. Verid
    # =========================================================================
    s14 = setup_slide(14)
    add_header(s14, "11. Why We Are Different: Traditional Storage vs. Verid", "Comparing passive document folders with an active, verified Digital Product Passport")

    # Table Card
    table_card = add_card(s14, 0.70, 1.65, 11.95, 5.00, WHITE, BORDER_LIGHT, 1)

    # Table Header Pills
    add_pill(s14, 0.90, 1.80, 2.50, 0.38, "DIMENSION", NAVY_DARK, WHITE, 10.5)
    add_pill(s14, 3.55, 1.80, 4.30, 0.38, "TRADITIONAL WARRANTY STORAGE", RGBColor(0x94, 0xA3, 0xB8), WHITE, 10.5)
    add_pill(s14, 8.00, 1.80, 4.45, 0.38, "VERID DIGITAL PRODUCT PASSPORT", GOLD, NAVY_DARK, 10.5)

    comp_rows = [
        ("Evidence Intake", "Manual PDF upload to Google Drive / folder", "Dual-Anchor: Commercial document + Real physical hardware photo"),
        ("Physical Proof", "NONE (Zero validation of actual hardware possession)", "Real-time Fine-Tuned Custom YOLOv8 computer vision detection"),
        ("Data Extraction", "Manual typing of serials, dates, and prices", "Sub-150ms RapidOCR + zero-fabrication deterministic regex parser"),
        ("Lifecycle Intel", "Passive date reminder (often missed or ignored)", "Proactive Smart Guardian: 30-day maintenance AI + warranty countdown"),
        ("Trust & Security", "Static unverified PDFs easily forged or altered", "Cryptographically sealed SHA-256 hash + EU Ecodesign DPP Certificate"),
        ("Phone Camera Role", "Passive document photography / file viewer", "Phone-first dynamic QR camera scanner for real-time asset matching"),
    ]
    ry = 2.30
    for dim, trad, verid in comp_rows:
        tb_r = s14.shapes.add_textbox(Inches(0.90), Inches(ry), Inches(11.55), Inches(0.65))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True

        p = tf_r.paragraphs[0]
        p.text = f"{dim.ljust(18)}  |  {trad[:45].ljust(48)}  |  ✓ {verid}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK

        # Add horizontal hairline
        hl = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.90), Inches(ry + 0.65), Inches(11.55), Inches(0.01))
        hl.fill.solid()
        hl.fill.fore_color.rgb = RGBColor(0xEE, 0xE8, 0xDA)
        hl.line.fill.background()

        ry += 0.70

    # =========================================================================
    # SLIDE 15: Future Vision: AI House Memory (Local & Private)
    # =========================================================================
    s15 = setup_slide(15)
    add_header(s15, "12. Future Vision / Next Evolution: AI House Memory", "“An AI that remembers your home, understands what is inside it, and helps you take care of it.”")

    # Left: Implemented Today
    add_bullet_card(s15, 0.70, 1.65, 5.80, 5.00, "IMPLEMENTED TODAY (PRODUCTION READY)", GREEN_TEAL, [
        "Dual-Evidence Digital Product Passports: Combines commercial and hardware proof.",
        "Fine-Tuned Custom YOLO Appliance Detector: 5 classes with 98.10% mAP@50.",
        "RapidOCR Document Parsing: Zero-fabrication regex extraction of serials and dates.",
        "Phone-First Wi-Fi QR Scanner: Instant pairing for iQOO / Android smartphones.",
        "Official EU DPP Certificate: SHA-256 sealed with Repairability Index (8.6/10).",
        "Proactive Smart Guardian: Automated warranty countdown and maintenance alerts.",
    ], "Engineered, Tested & Live in Codebase")

    # Right: Future Vision (Local Qwen Vision)
    add_bullet_card(s15, 6.85, 1.65, 5.80, 5.00, "NEXT EVOLUTION: AI HOUSE MEMORY (FUTURE VISION)", GOLD, [
        "Spatial Visual Memory: Remembers products, appliances, furniture, and where items belong.",
        "Temporal Change Detection: Tracks interior changes over time; notices missing or moved items.",
        "Interior & Asset Awareness: Remembers paint color codes, plumbing fixtures, and accessories.",
        "Predictive Household Care: Recommends filter replacements, descaling, and seasonal prep.",
        "100% Private Local Edge AI: Powered by local vision models (Ollama/Qwen3-VL) — intimate home imagery never leaves the household Wi-Fi network!",
    ], "Expanding Beyond Products into Home Memory")

    # =========================================================================
    # SLIDE 16: Live Demo Story & Judge Walkthrough
    # =========================================================================
    s16 = setup_slide(16)
    add_header(s16, "13. Live Demo Story: The 3-Minute Walkthrough", "A crisp, reproducible demonstration flow built specifically for hackathon judges")

    demo_steps = [
        ("01  OVERVIEW & GUARDIAN", "Minute 0:00 – 0:45", BLUE_ACCENT, [
            "Open Overview Dashboard.",
            "Inspect live statistics & Trust Center AI model health.",
            "Highlight the 3 Smart Guardian cards: Warranty Shield (100%), Maintenance AI, and EU DPP Score (94.8%).",
        ]),
        ("02  1-CLICK DUAL INTAKE", "Minute 0:45 – 1:30", GOLD, [
            "Navigate to 'Create Passport'.",
            "Tap 1-Click Electrolux Preset button.",
            "Instantly populates commercial warranty PDF + physical washing machine photo together.",
        ]),
        ("03  AI VERIFICATION", "Minute 1:30 – 2:15", GREEN_TEAL, [
            "RapidOCR extracts Serial, Model, Date, and Price in ~120ms with zero hallucination.",
            "Custom YOLO detects appliance with glowing bounding box and 95% confidence score.",
        ]),
        ("04  CERTIFICATE & PHONE", "Minute 2:15 – 3:00", BLUE_ACCENT, [
            "Open minted passport & click 'Official DPP Certificate' for exportable PDF seal.",
            "Click 'Connect Phone' to display dynamic QR code for instant mobile camera testing.",
        ]),
    ]
    dw = 2.85
    dgap = 0.18
    dx = 0.70
    for title, timing, color, points in demo_steps:
        add_card(s16, dx, 1.65, dw, 5.00, WHITE, BORDER_LIGHT, 1)
        add_pill(s16, dx + 0.15, 1.82, dw - 0.30, 0.35, title, color, WHITE, 9.5)

        tb_d = s16.shapes.add_textbox(Inches(dx + 0.15), Inches(2.28), Inches(dw - 0.30), Inches(4.20))
        tf_d = tb_d.text_frame
        tf_d.word_wrap = True

        p_t = tf_d.paragraphs[0]
        p_t.text = timing
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = GOLD
        p_t.space_after = Pt(8)

        for pt in points:
            p = tf_d.add_paragraph()
            p.text = f"• {pt}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_MUTED
            p.space_after = Pt(6)

        dx += dw + dgap

    # =========================================================================
    # SLIDE 17: Conclusion (Dark Theme)
    # =========================================================================
    s17 = setup_slide(17, is_dark=True)
    add_pill(s17, 0.88, 0.95, 3.40, 0.36, "iQOO HACKATHON 2026 • CONCLUSION", GOLD, NAVY_DARK, 10.5)

    tb17 = s17.shapes.add_textbox(Inches(0.85), Inches(1.48), Inches(11.50), Inches(0.85))
    tf17 = tb17.text_frame
    p17 = tf17.paragraphs[0]
    p17.text = "Verid: We Built It. We Proved It. It Scales."
    p17.font.name = FONT_HEADING
    p17.font.size = Pt(36)
    p17.font.bold = True
    p17.font.color.rgb = WHITE

    tb17_sub = s17.shapes.add_textbox(Inches(0.88), Inches(2.35), Inches(11.50), Inches(0.45))
    p17_sub = tb17_sub.text_frame.paragraphs[0]
    p17_sub.text = "A complete engineering system today — the foundation for private AI home memory tomorrow"
    p17_sub.font.size = Pt(15)
    p17_sub.font.color.rgb = RGBColor(0xD2, 0xDC, 0xE6)

    # 3 Conclusion Pillars
    pillars = [
        ("1. WE BUILT IT", BLUE_ACCENT, [
            "Complete working full-stack system running live locally.",
            "Vite 7 + React 19 web frontend with instant Phone QR scanner.",
            "FastAPI microservice executing Custom YOLOv8 and RapidOCR.",
            "Zero placeholder mockups: real working code on local hardware.",
        ]),
        ("2. WE PROVED IT", GREEN_TEAL, [
            "98.10% mAP@50 and 99.29% precision validation results.",
            "12 real project screenshots proving every step of intake and verification.",
            "Strict zero-fabrication parsing preventing hallucinated identifiers.",
            "Cryptographic SHA-256 deterministic sealing of passport records.",
        ]),
        ("3. IT SCALES BIGGER", GOLD, [
            "Digital Product Passport solves the immediate $10B warranty problem.",
            "Local Qwen3-VL vision evolves into on-device AI House Memory.",
            "Understands household changes, furniture, and maintenance needs.",
            "100% private: intimate domestic imagery stays on the local device.",
        ]),
    ]
    pw = 3.75
    pgap = 0.35
    px = 0.88
    for title, color, points in pillars:
        add_card(s17, px, 3.00, pw, 3.00, NAVY_CARD, color, 1.5)
        add_pill(s17, px + 0.15, 3.15, pw - 0.30, 0.35, title, color, WHITE, 11)

        tb_p = s17.shapes.add_textbox(Inches(px + 0.15), Inches(3.65), Inches(pw - 0.30), Inches(2.20))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True

        for i, pt in enumerate(points):
            p = tf_p.paragraphs[0] if i == 0 else tf_p.add_paragraph()
            p.text = f"✓  {pt}"
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_LIGHT
            p.space_after = Pt(4)

        px += pw + pgap

    # Team & Links
    tb_team = s17.shapes.add_textbox(Inches(0.88), Inches(6.15), Inches(11.50), Inches(0.50))
    p_team = tb_team.text_frame.paragraphs[0]
    p_team.text = "Team Verid • GitHub Repository: https://github.com/ATS-AI-6278/IQ-Hackathon • Ready for Judging Q&A"
    p_team.font.bold = True
    p_team.font.size = Pt(12)
    p_team.font.color.rgb = GOLD

    # Save to file
    output_path = "Smart_Product_Passport_Project_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation successfully generated and saved to {output_path} ({TOTAL_SLIDES} slides).")

if __name__ == "__main__":
    build_presentation()
