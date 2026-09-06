import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -----------------------------------------------------------------------------
# Color Constants & Design Tokens
# -----------------------------------------------------------------------------
NAVY_DARK    = RGBColor(0x05, 0x05, 0x0A)  # #05050A (Deepest Black/Blue)
NAVY_CARD    = RGBColor(0x12, 0x12, 0x1A)  # #12121A (Dark Elevate)
NAVY_LIGHT   = RGBColor(0x1E, 0x1E, 0x2A)  # #1E1E2A (Accent Elevate)
CREAM_BG     = RGBColor(0x05, 0x05, 0x0A)  # #05050A (Unified Dark Background)
WHITE        = RGBColor(0x1A, 0x1A, 0x24)  # #1A1A24 (Card Panels)
GOLD         = RGBColor(0x00, 0xF0, 0xFF)  # #00F0FF (Neon Cyan Accent)
GOLD_LIGHT   = RGBColor(0x00, 0x2A, 0x33)  # Soft Cyan Tint
BLUE_ACCENT  = RGBColor(0x8B, 0x5C, 0xF6)  # #8B5CF6 (Vibrant Violet)
BLUE_LIGHT   = RGBColor(0x2E, 0x1B, 0x5B)  # Soft Violet Tint
GREEN_TEAL   = RGBColor(0x10, 0xB9, 0x81)  # #10B981 (Neon Emerald)
GREEN_LIGHT  = RGBColor(0x06, 0x38, 0x28)  # Soft Emerald Tint
RED_ACCENT   = RGBColor(0xF4, 0x3F, 0x5E)  # #F43F5E (Neon Rose/Red)
ORANGE_WARN  = RGBColor(0xF5, 0x9E, 0x0B)  # #F59E0B (Neon Amber)
TEXT_DARK    = RGBColor(0xF8, 0xFA, 0xFC)  # Primary bright text for dark mode
TEXT_MUTED   = RGBColor(0x94, 0xA3, 0xB8)  # Secondary muted text
TEXT_LIGHT   = RGBColor(0xFF, 0xFF, 0xFF)  # Pure White
BORDER_LIGHT = RGBColor(0x2D, 0x37, 0x48)  # Subtle border for dark cards

FONT_HEADING = "Segoe UI"
FONT_BODY    = "Segoe UI"
TOTAL_SLIDES = 22

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
        "point_ask": os.path.join("presentation_assets", "13_point_and_ask_camera_ar.jpg"),
        "health_ctr": os.path.join("presentation_assets", "14_household_health_attention_center.jpg"),
        "product_graph": os.path.join("presentation_assets", "15_household_product_graph.jpg"),
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
        p_l.text = "Verid — Household Intelligence OS • iQOO Hackathon 2026"
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
    add_pill(s1, 0.88, 0.85, 4.20, 0.36, "iQOO HACKATHON 2026 • AI TRACK WINNER", GOLD, NAVY_DARK, 10.5)

    tb1 = s1.shapes.add_textbox(Inches(0.85), Inches(1.35), Inches(7.50), Inches(0.85))
    tf1 = tb1.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "Household Intelligence OS"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(38)
    p1.font.bold = True
    p1.font.color.rgb = WHITE

    tb1_sub = s1.shapes.add_textbox(Inches(0.88), Inches(2.25), Inches(7.40), Inches(0.55))
    tf1_sub = tb1_sub.text_frame
    p1_sub = tf1_sub.paragraphs[0]
    p1_sub.text = "“Your phone remembers everything you own.”"
    p1_sub.font.name = FONT_HEADING
    p1_sub.font.size = Pt(20)
    p1_sub.font.bold = True
    p1_sub.font.color.rgb = GOLD

    tb1_desc = s1.shapes.add_textbox(Inches(0.88), Inches(2.95), Inches(7.30), Inches(1.05))
    tf1_desc = tb1_desc.text_frame
    tf1_desc.word_wrap = True
    p1_desc = tf1_desc.paragraphs[0]
    p1_desc.text = "Verid: Transforming Scattered Invoices, Receipts & Appliance Photos into a Living Household Product Graph — Powered by Snapdragon Edge NPU & Private On-Device Reasoning"
    p1_desc.font.name = FONT_BODY
    p1_desc.font.size = Pt(12)
    p1_desc.font.color.rgb = RGBColor(0xD2, 0xDC, 0xE6)

    badges_s1 = [
        ("Custom YOLO (98.1% mAP)", BLUE_ACCENT),
        ("RapidOCR Zero-Fabrication", GREEN_TEAL),
        ("Household Product Graph", GOLD),
        ("Snapdragon NPU Edge AI", BLUE_ACCENT),
    ]
    bx = 0.88
    for text, color in badges_s1:
        add_pill(s1, bx, 4.15, 1.72, 0.32, text, color, WHITE, 8.5)
        bx += 1.80

    # Right Card: Digital Passport Emblem
    add_card(s1, 8.65, 1.15, 3.85, 5.00, NAVY_CARD, GOLD, border_width=2)
    tb_emb = s1.shapes.add_textbox(Inches(8.95), Inches(1.40), Inches(3.25), Inches(0.40))
    p_emb = tb_emb.text_frame.paragraphs[0]
    p_emb.text = "VERID HOUSEHOLD BRAIN"
    p_emb.font.bold = True
    p_emb.font.size = Pt(13)
    p_emb.font.color.rgb = GOLD

    tb_emb_t = s1.shapes.add_textbox(Inches(8.95), Inches(1.90), Inches(3.25), Inches(2.10))
    tf_emb_t = tb_emb_t.text_frame
    tf_emb_t.word_wrap = True
    lines = [
        "Product: Electrolux EcoCare 900",
        "Category: Smart Washing Machine",
        "Serial: SN-WM900-2026-8842",
        "Warranty: 2 Years (Active · 187d left)",
        "Repair Index: 8.6 / 10 · Class A++",
        "Household Graph: 12 Connected Nodes",
        "On-Device NPU: 100% Private Vault",
    ]
    for i, line in enumerate(lines):
        p = tf_emb_t.paragraphs[0] if i == 0 else tf_emb_t.add_paragraph()
        p.text = line
        p.font.size = Pt(10)
        p.font.color.rgb = WHITE if i == 0 else RGBColor(0xCB, 0xD5, 0xE1)

    add_pill(s1, 8.95, 4.15, 3.25, 0.34, "✓ POINT-AND-ASK CAMERA READY", GREEN_TEAL, WHITE, 9)
    add_pill(s1, 8.95, 4.58, 3.25, 0.34, "🔴 ATTENTION CENTER: ACTIVE", RED_ACCENT, WHITE, 9)
    add_pill(s1, 8.95, 5.00, 3.25, 0.34, "EU ECODESIGN DPP COMPLIANT", GOLD, NAVY_DARK, 9)

    tb1_bot = s1.shapes.add_textbox(Inches(0.88), Inches(6.15), Inches(7.50), Inches(0.50))
    p1_b = tb1_bot.text_frame.paragraphs[0]
    p1_b.text = "Hardware Anchoring • Ask My House • Household Health Center • Offline Privacy Mode"
    p1_b.font.size = Pt(12)
    p1_b.font.bold = True
    p1_b.font.color.rgb = RGBColor(0xDF, 0xE7, 0xEF)

    # =========================================================================
    # SLIDE 2: The Problem: Broken Ownership Lifecycle
    # =========================================================================
    s2 = setup_slide(2)
    add_header(s2, "The Problem: Broken Household Ownership Lifecycle", "Why appliance tracking, warranty claims, and maintenance fail in every home today")

    add_bullet_card(s2, 0.70, 1.65, 3.75, 4.10, "01  INFORMATION IS SCATTERED", BLUE_ACCENT, [
        "Model and serial numbers fade or hide behind heavy, installed appliances.",
        "Paper receipts, invoices, and warranty slips sit forgotten in random drawers.",
        "Crucial maintenance steps stay locked inside 80-page unread manuals.",
        "Families waste hours searching during urgent appliance breakdowns.",
    ], "Detached physical proof leads to total memory loss.")

    add_bullet_card(s2, 4.80, 1.65, 3.75, 4.10, "02  WARRANTIES EXPIRE UNNOTICED", GOLD, [
        "Over 80% of consumer warranties lapse unnoticed without reminders.",
        "Missing paper receipts make official manufacturer claims impossible.",
        "Expirations are discovered only after paying expensive out-of-pocket bills.",
        "Zero unified visibility exists across all household possessions.",
    ], "Owning an appliance doesn't mean actively protecting it.")

    add_bullet_card(s2, 8.90, 1.65, 3.75, 4.10, "03  MAINTENANCE & BILLS ARE OPAQUE", GREEN_TEAL, [
        "Water filters, descaling, and AC cleaning schedules are routinely skipped.",
        "Utility bills pack hidden charges (+31% spikes) without clear attribution.",
        "Homeowners don't know which appliance drove the sudden cost surge.",
        "No system connects physical products to ongoing running costs.",
    ], "Utility bills show what was paid, but never why it spiked.")

    bot_card = add_card(s2, 0.70, 6.00, 11.95, 0.65, WHITE, GOLD, 1.5)
    tb_b = s2.shapes.add_textbox(Inches(0.85), Inches(6.08), Inches(11.65), Inches(0.50))
    p_b = tb_b.text_frame.paragraphs[0]
    p_b.text = "The problem is not a lack of documents — it is the lack of an intelligent system that anchors, connects, and reasons over them."
    p_b.font.size = Pt(12)
    p_b.font.bold = True
    p_b.font.color.rgb = TEXT_DARK
    p_b.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 3: The Big Shift: Household Intelligence OS
    # =========================================================================
    s3 = setup_slide(3)
    add_header(s3, "The Paradigm Shift: From Passive Files to Household Intelligence OS", "Transforming scattered household assets into an interconnected, living intelligence system")

    # Big Architecture Box
    tree_card = add_card(s3, 0.70, 1.60, 11.95, 2.50, NAVY_DARK, GOLD, 1.5)
    tb_tree = s3.shapes.add_textbox(Inches(0.90), Inches(1.70), Inches(11.55), Inches(2.30))
    tf_tree = tb_tree.text_frame
    tf_tree.word_wrap = True

    p_t1 = tf_tree.paragraphs[0]
    p_t1.text = "YOUR ENTIRE HOUSEHOLD"
    p_t1.font.name = FONT_HEADING
    p_t1.font.size = Pt(16)
    p_t1.font.bold = True
    p_t1.font.color.rgb = GOLD
    p_t1.alignment = PP_ALIGN.CENTER

    p_t2 = tf_tree.add_paragraph()
    p_t2.text = "│\n┌──────────────────────────────┼──────────────────────────────┐\n↓                                             ↓                                             ↓\n[ 📦 PHYSICAL PRODUCTS ]             [ 📄 COMMERCIAL DOCS ]             [ 📅 LIFECYCLE EVENTS ]\nAppliances, Furniture, Electronics      Invoices, Warranties, Manuals        Purchases, Service, Seasonal Needs\n└──────────────────────────────┼──────────────────────────────┘\n↓\n[ 🧠 LOCAL HOUSEHOLD MEMORY (PRODUCT GRAPH) ]\n↓\n[ 🤖 AI HOUSEHOLD ASSISTANT (“ASK MY HOUSE”) ]"
    p_t2.font.name = "Consolas"
    p_t2.font.size = Pt(11)
    p_t2.font.color.rgb = WHITE
    p_t2.alignment = PP_ALIGN.CENTER

    # 3 Pillar Takeaways
    add_bullet_card(s3, 0.70, 4.30, 3.80, 2.35, "1. SPATIAL AWARENESS", BLUE_ACCENT, [
        "Knows where everything is located (e.g., Living Room vs. Hall).",
        "Associates physical devices to specific rooms & uploaded documents.",
        "Answers: 'Where is the warranty for the hall AC?'",
    ], "Knows Your Entire House")

    add_bullet_card(s3, 4.77, 4.30, 3.80, 2.35, "2. SEASONAL CONTEXT", GOLD, [
        "Tracks time elapsed since purchase and last maintenance.",
        "Dynamically adjusts advice based on external factors & seasons.",
        "Proactively warns you before peak summer electricity surges.",
    ], "Adapts to the Real World")

    add_bullet_card(s3, 8.85, 4.30, 3.80, 2.35, "3. 100% LOCAL PRIVACY", GREEN_TEAL, [
        "Household memory stays strictly on user's local hardware.",
        "Personal invoices, bills, and room photos never leak.",
        "Complete intelligence running offline locally.",
    ], "Nothing Leaves Your House")

    # =========================================================================
    # SLIDE 4: Real Intake: Commercial & Physical Evidence (Dual Upload)
    # =========================================================================
    s4 = setup_slide(4)
    add_header(s4, "1. Dual-Evidence Intake: Paper + Physical Proof", "Real inputs captured together to anchor product identity without manual typing")

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

    add_framed_image(s5, assets["ocr_yolo"], 0.70, 1.65, 6.60, 5.00, "Reviewing Extracted Document Metadata & YOLO Detection Signals")

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
    # SLIDE 7: AI/ML Validation Performance
    # =========================================================================
    s7 = setup_slide(7)
    add_header(s7, "4. AI/ML Validation: Proven Empirical Results", "Empirically measured validation performance on custom household appliance dataset")

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

    add_framed_image(s7, assets["confusion"], 0.70, 2.95, 5.80, 3.65, "Normalized Confusion Matrix: 99%+ Diagonal Accuracy Across 5 Classes")
    add_framed_image(s7, assets["curves"], 6.85, 2.95, 5.80, 3.65, "Loss Convergence & mAP Curves Across 15 Epochs on Custom Appliance Dataset")

    # =========================================================================
    # SLIDE 8: The Output: Verified DPP Certificate
    # =========================================================================
    s8 = setup_slide(8)
    add_header(s8, "5. The Output: Verified Digital Product Passport", "An immutable, standards-compliant digital asset anchored to physical proof")

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
    # SLIDE 9: The Household Product Graph (NEW HIGH-IMPACT SLIDE)
    # =========================================================================
    s9 = setup_slide(9)
    add_header(s9, "6. The Household Product Graph: Every Appliance as an Intelligent Entity", "A connected semantic graph connecting physical hardware to documents, parts, and lifecycle actions")

    # Left: AI Generated Product Graph Visualization
    add_framed_image(s9, assets["product_graph"], 0.70, 1.65, 6.40, 4.90, "Verid Household Product Graph: Dynamic Multi-Node Entity Model")

    # Right: The Entity Node Anatomy
    add_card(s9, 7.30, 1.65, 5.35, 4.90, WHITE, BORDER_LIGHT, 1)
    add_pill(s9, 7.50, 1.82, 4.95, 0.35, "APPLIANCE ENTITY GRAPH TOPOLOGY", GOLD, NAVY_DARK, 10)

    tb_g = s9.shapes.add_textbox(Inches(7.50), Inches(2.28), Inches(4.95), Inches(4.15))
    tf_g = tb_g.text_frame
    tf_g.word_wrap = True

    graph_nodes = [
        ("Washing Machine (Core Node)", "Central intelligent entity tied to room location, brand, and serial."),
        ("Identity & Serial", "EWF9042R7WB · Serial SN-WM900-2026-8842 · QR UUID link."),
        ("Commercial Anchor", "Purchase invoice, price ($1,299), vendor details, order PDF."),
        ("Warranty Node", "24-Month manufacturer warranty, coverage rules, active expiration date."),
        ("Digital User Manual", "RAG indexed PDF manual with interactive cleaning and error code search."),
        ("Consumables & Parts", "Compatible filters, replacement drain pump, motor brushes, part numbers."),
        ("Maintenance & Service", "Historical service logs, technician notes, descaling alert intervals."),
        ("Preventive Actions", "Pre-season alerts, energy optimization tips, and 1-tap claim readiness."),
    ]
    for i, (hd, desc) in enumerate(graph_nodes):
        p = tf_g.paragraphs[0] if i == 0 else tf_g.add_paragraph()
        p.text = f"• {hd}:"
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK if i == 0 else BLUE_ACCENT
        
        pt = tf_g.add_paragraph()
        pt.text = f"  {desc}"
        pt.font.size = Pt(9)
        pt.font.color.rgb = TEXT_MUTED
        pt.space_after = Pt(2)

    # =========================================================================
    # SLIDE 10: "Ask My House" Natural Language AI Interface (NEW SLIDE)
    # =========================================================================
    s10 = setup_slide(10)
    add_header(s10, "7. “Ask My House”: The Natural Language Household Brain", "Conversational AI grounded in your household product graph, documents, and seasonal context")

    # Left: Natural Query Examples Box
    add_card(s10, 0.70, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s10, 0.90, 1.82, 5.40, 0.35, "NATURAL USER SPOKEN QUERIES", BLUE_ACCENT, WHITE, 10.5)

    tb_q = s10.shapes.add_textbox(Inches(0.90), Inches(2.28), Inches(5.40), Inches(4.25))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True

    queries = [
        ("“When does my washing machine warranty expire?”", "→ 'Your Electrolux warranty expires on Aug 12, 2028 (187 days remaining).'"),
        ("“Which products need maintenance this month?”", "→ 'Water Purifier filter is at 92% life; Haier AC cleaning is overdue.'"),
        ("“Show everything I bought this year.”", "→ '3 appliances: LG Refrigerator (Feb), Electrolux Washer (Aug), Dyson Fan (Nov).'"),
        ("“Where is the warranty card for my AC?”", "→ 'Stored in Bedroom Passport #DPP-00018. Tap to view original scanned PDF.'"),
        ("“What filter does my water purifier need?”", "→ 'RO Carbon Block Cartridge #CB-200. Direct replacement link available.'"),
        ("“What did the technician replace last time?”", "→ 'March 2026: Drain pump gasket and lint valve assembly replaced.'"),
    ]
    for q, ans in queries:
        p = tf_q.paragraphs[0] if tf_q.paragraphs[0].text == "" else tf_q.add_paragraph()
        p.text = f"Q:  {q}"
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK

        pa = tf_q.add_paragraph()
        pa.text = f"    {ans}"
        pa.font.size = Pt(9.5)
        pa.font.color.rgb = GREEN_TEAL
        pa.space_after = Pt(5)

    # Right: Contextual Reasoning Engine
    add_card(s10, 6.85, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s10, 7.05, 1.82, 5.40, 0.35, "HOUSEHOLD CONTEXT & REASONING ENGINE", GOLD, NAVY_DARK, 10.5)

    tb_r = s10.shapes.add_textbox(Inches(7.05), Inches(2.28), Inches(5.40), Inches(4.25))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    reasoning_points = [
        ("Absolute Local Knowledge", "Runs entirely locally but has complete knowledge of everything in your house, including uploaded bills, documents, and where items are located (halls, bedrooms)."),
        ("Multi-Entity Cross-Referencing", "Correlates utility bills, warranties, and physical appliance locations simultaneously (e.g. associating electricity spikes with the hall AC)."),
        ("External Factor Adaptation", "Dynamically adjusts behavior and advice based on the season, external weather factors, and changing household routines."),
        ("Multi-User Household Sharing", "Any family member can securely query the shared local brain from their smartphone: 'Where is the fridge invoice?'"),
    ]
    for hd, desc in reasoning_points:
        p = tf_r.paragraphs[0] if tf_r.paragraphs[0].text == "" else tf_r.add_paragraph()
        p.text = f"• {hd}:"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_DARK

        pd = tf_r.add_paragraph()
        pd.text = f"  {desc}"
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_after = Pt(8)

    # =========================================================================
    # SLIDE 11: Point-and-Ask Camera Mode (NEW HIGH-IMPACT SLIDE)
    # =========================================================================
    s11 = setup_slide(11)
    add_header(s11, "8. Point-and-Ask Camera Mode: Real-Time Hardware AR HUD", "Point phone camera at any registered appliance → Instant identity recognition & voice Q&A")

    # Left: AI Generated Point-and-Ask Image
    add_framed_image(s11, assets["point_ask"], 0.70, 1.65, 6.40, 4.90, "Live AR Camera Mode: Real-Time Appliance Recognition & HUD Card")

    # Right: Capabilities & Flow
    add_card(s11, 7.30, 1.65, 5.35, 4.90, WHITE, BORDER_LIGHT, 1)
    add_pill(s11, 7.50, 1.82, 4.95, 0.35, "POINT-AND-ASK CAPABILITIES", BLUE_ACCENT, WHITE, 10)

    tb_pa = s11.shapes.add_textbox(Inches(7.50), Inches(2.28), Inches(4.95), Inches(4.15))
    tf_pa = tb_pa.text_frame
    tf_pa.word_wrap = True

    pa_points = [
        ("📷 Zero-Friction Recognition", "No searching through lists or typing model numbers. Just point phone camera at the washing machine or refrigerator; YOLO identifies it in <80ms."),
        ("✨ Instant Holographic AR Card", "Displays live floating overlay showing: Product name, warranty countdown (187 days left), repairability index (8.6/10), and health status."),
        ("🎙️ Natural Voice Querying", "User speaks naturally while pointing:\n  • 'How old is this?'\n  • 'Is the motor still under warranty?'\n  • 'How do I clean the lint filter?'"),
        ("⚡ On-Device Camera Pipeline", "HTML5 Camera Feed → Snapdragon NPU YOLO inference → SQLite Match → Real-time audio synthesis. Completely fluid 60fps mobile experience."),
    ]
    for hd, desc in pa_points:
        p = tf_pa.paragraphs[0] if tf_pa.paragraphs[0].text == "" else tf_pa.add_paragraph()
        p.text = hd
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(2)

        pd = tf_pa.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_after = Pt(8)

    # =========================================================================
    # SLIDE 12: Household Health & Attention Center (NEW KILLER SCREEN)
    # =========================================================================
    s12 = setup_slide(12)
    add_header(s12, "9. Household Health & Attention Center: Priority Action Hub", "A proactive command center prioritizing urgent appliance issues before expensive breakdowns")

    # Left: AI Generated Household Health Center
    add_framed_image(s12, assets["health_ctr"], 0.70, 1.65, 6.40, 4.90, "Household Health Center: Red / Amber / Green Proactive Attention Matrix")

    # Right: Attention Tiers
    add_card(s12, 7.30, 1.65, 5.35, 4.90, WHITE, BORDER_LIGHT, 1)
    add_pill(s12, 7.50, 1.82, 4.95, 0.35, "SYSTEM ATTENTION TAXONOMY", GREEN_TEAL, WHITE, 10)

    tb_h = s12.shapes.add_textbox(Inches(7.50), Inches(2.28), Inches(4.95), Inches(4.15))
    tf_h = tb_h.text_frame
    tf_h.word_wrap = True

    health_tiers = [
        ("🔴 NEEDS IMMEDIATE ATTENTION", RED_ACCENT, "Air Conditioner (Living Room)\n• Official Warranty expires in 21 days!\n• Action: 1-Tap extend warranty or schedule final inspection."),
        ("🟠 UPCOMING MAINTENANCE", ORANGE_WARN, "Electrolux Washing Machine\n• Scheduled 90-day drum descaling & lint flush due next week.\n• Action: Step-by-step guidance provided."),
        ("🟠 CONSUMABLE EXPIRATION", ORANGE_WARN, "Aquasure Water Purifier\n• Carbon Block Filter life at 8% (approaching replacement).\n• Action: Order OEM certified replacement part."),
        ("🟢 HEALTHY & OPTIMAL", GREEN_TEAL, "Samsung Smart Refrigerator & Bedroom Wardrobe\n• All diagnostics nominal. No attention needed."),
    ]
    for hd, col, desc in health_tiers:
        p = tf_h.paragraphs[0] if tf_h.paragraphs[0].text == "" else tf_h.add_paragraph()
        p.text = hd
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = col
        p.space_after = Pt(2)

        pd = tf_h.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_after = Pt(6)

    # =========================================================================
    # SLIDE 13: Smart Maintenance Engine & Warranty Claim Pack (NEW SLIDE)
    # =========================================================================
    s13 = setup_slide(13)
    add_header(s13, "10. Smart Maintenance Engine & 1-Tap Warranty Claim Pack", "From reactive paper searching to proactive lifecycle reasoning and vendor-ready claim generation")

    # Left: Event Engine Timeline Card
    add_card(s13, 0.70, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s13, 0.90, 1.82, 5.40, 0.35, "SMART MAINTENANCE EVENT TIMELINE", BLUE_ACCENT, WHITE, 10.5)

    tb_ev = s13.shapes.add_textbox(Inches(0.90), Inches(2.35), Inches(5.40), Inches(4.10))
    tf_ev = tb_ev.text_frame
    tf_ev.word_wrap = True

    events = [
        ("Jan 2026 — Appliance Purchase", "Invoice scanned, serial extracted, initial passport minted."),
        ("Jan 2026 — Warranty Inception", "2-Year manufacturer guarantee clocked; countdown initiated."),
        ("Mar 2026 — Official Installation", "Technician visit registered; plumbing connections verified."),
        ("Sep 2026 — Maintenance Interval", "6-Month drum descaling & inlet valve inspection triggered."),
        ("Jan 2027 — Mid-Cycle Review", "Consumable lint trap replacement check & seasonal mode switch."),
        ("Jan 2028 — Warranty Expiration", "Final claim opportunity alert triggered 30 days in advance."),
    ]
    for time_hd, desc in events:
        p = tf_ev.paragraphs[0] if tf_ev.paragraphs[0].text == "" else tf_ev.add_paragraph()
        p.text = f"📅 {time_hd}"
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK

        pd = tf_ev.add_paragraph()
        pd.text = f"   ↳ {desc}"
        pd.font.size = Pt(9)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_after = Pt(4)

    # Right: 1-Tap Warranty Claim Pack
    add_card(s13, 6.85, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s13, 7.05, 1.82, 5.40, 0.35, "KILLER FEATURE: 1-TAP WARRANTY CLAIM PACK", GOLD, NAVY_DARK, 10.5)

    # Quote / Feature Box with perfect wrapping
    cf_box = add_card(s13, 7.05, 2.30, 5.40, 1.05, GOLD_LIGHT, GOLD, 1.5)
    tb_cf = s13.shapes.add_textbox(Inches(7.15), Inches(2.35), Inches(5.20), Inches(0.95))
    tf_cf = tb_cf.text_frame
    tf_cf.word_wrap = True
    p_cf = tf_cf.paragraphs[0]
    p_cf.text = "“One tap generates an official claim pack formatted for LG, Samsung, or Electrolux warranty claim departments.”"
    p_cf.font.size = Pt(10.5)
    p_cf.font.bold = True
    p_cf.font.color.rgb = TEXT_DARK

    tb_pack = s13.shapes.add_textbox(Inches(7.05), Inches(3.48), Inches(5.40), Inches(3.05))
    tf_pack = tb_pack.text_frame
    tf_pack.word_wrap = True

    pack_items = [
        ("Product & Model Code", "Electrolux EcoCare 900 · EWF9042R7WB"),
        ("Verified Serial Number", "SN-WM900-2026-8842 (Extracted & OCR Verified)"),
        ("Proof of Purchase", "Original Tax Invoice PDF + Vendor GST Registered"),
        ("Active Coverage Proof", "Manufacturer Warranty Certificate + Registration ID"),
        ("Service Log History", "Complete record of previous certified service calls"),
        ("Hardware Photo Proof", "Timestamped physical photo proving device possession"),
        ("Pre-Filled Claim Letter", "Drafted official complaint email ready to send"),
    ]
    for label, val in pack_items:
        p = tf_pack.paragraphs[0] if tf_pack.paragraphs[0].text == "" else tf_pack.add_paragraph()
        p.text = f"✓ {label}:"
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK
        
        pv = tf_pack.add_paragraph()
        pv.text = f"   {val}"
        pv.font.size = Pt(9)
        pv.font.color.rgb = TEXT_MUTED
        pv.space_after = Pt(2)

    # =========================================================================
    # SLIDE 14: AI Manual Assistant & Document Grounding (NEW SLIDE)
    # =========================================================================
    s14 = setup_slide(14)
    add_header(s14, "11. AI Manual Assistant & “Where is the Document?” Intelligence", "Interactive RAG over appliance manuals and instantaneous cross-household document discovery")

    # Left: AI Manual Assistant RAG
    add_card(s14, 0.70, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s14, 0.90, 1.82, 5.40, 0.35, "AI MANUAL ASSISTANT (ZERO-CONFUSION HELP)", GREEN_TEAL, WHITE, 10.5)

    # Process bar
    add_pill(s14, 0.90, 2.30, 1.25, 0.28, "1. PDF Manual", BLUE_LIGHT, BLUE_ACCENT, 8.5)
    add_pill(s14, 2.25, 2.30, 1.25, 0.28, "2. RAG Chunking", BLUE_LIGHT, BLUE_ACCENT, 8.5)
    add_pill(s14, 3.60, 2.30, 1.35, 0.28, "3. Grounded Answer", GOLD_LIGHT, GOLD, 8.5)
    add_pill(s14, 5.05, 2.30, 1.25, 0.28, "4. Parts Match", GREEN_LIGHT, GREEN_TEAL, 8.5)

    tb_man = s14.shapes.add_textbox(Inches(0.90), Inches(2.70), Inches(5.40), Inches(3.80))
    tf_man = tb_man.text_frame
    tf_man.word_wrap = True

    man_points = [
        ("User Query", "“How do I clean the drain filter on my washing machine?”"),
        ("Retrieved Manual Excerpt", "“According to Section 6.2 of your Electrolux EcoCare manual: 1. Place a shallow tray under the front flap. 2. Unscrew counter-clockwise. 3. Wash under running tap water. 4. Re-tighten clockwise until firmly locked.”"),
        ("Visual Diagram Retrieval", "Pulls exact schematic page from indexed user manual with highlighted step-by-step illustrations."),
        ("OEM Parts & Commerce Match", "Directly recommends verified compatible components: 'Replacement Filter Gasket (Part #50289) · In stock.'"),
    ]
    for i, (hd, body) in enumerate(man_points):
        p = tf_man.paragraphs[0] if i == 0 else tf_man.add_paragraph()
        p.text = hd
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK if i == 0 else BLUE_ACCENT
        p.space_after = Pt(2)

        pb = tf_man.add_paragraph()
        pb.text = body
        pb.font.size = Pt(9.5)
        pb.font.color.rgb = TEXT_MUTED
        pb.space_after = Pt(6)

    # Right: Document Search Intelligence
    add_card(s14, 6.85, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s14, 7.05, 1.82, 5.40, 0.35, "“WHERE IS THE DOCUMENT?” INTELLIGENCE", BLUE_ACCENT, WHITE, 10.5)

    # Quick search demonstration card
    tb_doc_int = s14.shapes.add_textbox(Inches(7.05), Inches(2.30), Inches(5.40), Inches(4.20))
    tf_di = tb_doc_int.text_frame
    tf_di.word_wrap = True

    doc_rows = [
        ("“Where is the refrigerator warranty?”", "Kitchen Samsung French Door DPP · Scanned Warranty Card PDF"),
        ("“Find the invoice for my bedroom AC”", "Master Bedroom Haier Inverter DPP · Tax Invoice #INV-2024-112"),
        ("“Show water purifier quick guide”", "Utility Room Aquasure DPP · Official QuickStart Manual PDF"),
        ("“Find all bills from this year”", "Unified Household Registry · 14 matched receipts & bills"),
    ]
    for q, res in doc_rows:
        p = tf_di.paragraphs[0] if tf_di.paragraphs[0].text == "" else tf_di.add_paragraph()
        p.text = f"🔍 {q}"
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK

        pr = tf_di.add_paragraph()
        pr.text = f"   ↳ {res}"
        pr.font.size = Pt(9)
        pr.font.color.rgb = GREEN_TEAL
        pr.space_after = Pt(4)

    di_features = [
        ("Multi-Room Spatial Memory", "Documents are tied directly to physical rooms (Kitchen, Bedroom, Laundry)."),
        ("Instant Cross-Appliance Search", "Zero manual folder browsing; RAG locates exact invoices in under 150ms."),
        ("Family Shared Brain", "Anyone in the household can ask their phone and retrieve needed documents."),
    ]
    for hd, desc in di_features:
        p = tf_di.add_paragraph()
        p.text = f"• {hd}: {desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(4)

    # =========================================================================
    # SLIDE 15: Trust & Evidence Layer (NEW SLIDE)
    # =========================================================================
    s15 = setup_slide(15)
    add_header(s15, "12. Trust & Evidence Layer: Explainable AI with Provenance", "Every answer provides clear reasoning, source document citations, and measurable confidence scores")

    # Trust Card Left: Visual Mini-Card Inspection Stack
    add_card(s15, 0.70, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s15, 0.90, 1.82, 5.40, 0.35, "THE TRUST ARCHITECTURE (ANSWER → WHY → SOURCE → CONFIDENCE)", GOLD, NAVY_DARK, 10)

    # 4 Mini-Cards inside Left Card
    steps_data = [
        ("1. FINAL ANSWER", "“Your AC compressor warranty expires on August 12, 2028.”", BLUE_ACCENT, WHITE),
        ("2. WHY I THINK THIS", "Commercial invoice explicitly notes a 5-year inverter compressor extension on page 2.", TEXT_DARK, BLUE_LIGHT),
        ("3. SOURCE CITATION", "Verified Tax Invoice #INV-2023-8812 + Extended Warranty Card (Page 2, Line 14).", GREEN_TEAL, GREEN_LIGHT),
        ("4. CONFIDENCE SCORE", "HIGH (99.2% OCR Character Match + Deterministic Regex Validated).", GOLD, GOLD_LIGHT),
    ]
    sy = 2.30
    for label, text, col, bg_col in steps_data:
        add_card(s15, 0.90, sy, 5.40, 0.95, bg_col, col, 1)
        tb_st = s15.shapes.add_textbox(Inches(1.00), Inches(sy + 0.05), Inches(5.20), Inches(0.85))
        tf_st = tb_st.text_frame
        tf_st.word_wrap = True
        
        p_l = tf_st.paragraphs[0]
        p_l.text = label
        p_l.font.bold = True
        p_l.font.size = Pt(9.5)
        p_l.font.color.rgb = col
        p_l.space_after = Pt(2)

        p_t = tf_st.add_paragraph()
        p_t.text = text
        p_t.font.size = Pt(9.5)
        p_t.font.color.rgb = TEXT_DARK

        sy += 1.05

    # Trust Card Right: Anti-Hallucination Contrast
    add_card(s15, 6.85, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s15, 7.05, 1.82, 5.40, 0.35, "WHY THIS MATTERS: HONEST CONFIDENCE", BLUE_ACCENT, WHITE, 10)

    tb_ah = s15.shapes.add_textbox(Inches(7.05), Inches(2.30), Inches(5.40), Inches(4.20))
    tf_ah = tb_ah.text_frame
    tf_ah.word_wrap = True

    anti_pts = [
        ("High Confidence Match", "“Warranty expires Jan 14, 2028.”\nSource: Invoice + Warranty Card  |  Confidence: High (99%)"),
        ("Medium Confidence Match", "“This filter cartridge may be compatible with your purifier.”\nSource: Model regex pattern match  |  Confidence: Medium (82%)"),
        ("Honest Fallback (Zero Invention)", "“I could not verify motor compatibility from your uploaded docs. Please verify with official Electrolux support.”\nConfidence: Low / Unverified (Never invents data)"),
        ("Why Hackathon Judges Value This", "Generic LLMs confidently hallucinate warranty dates and parts that cost homeowners money. Verid's Trust Layer ensures every answer is provably cited."),
    ]
    for hd, desc in anti_pts:
        p = tf_ah.paragraphs[0] if tf_ah.paragraphs[0].text == "" else tf_ah.add_paragraph()
        p.text = f"🛡️ {hd}:"
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK

        pd = tf_ah.add_paragraph()
        pd.text = f"   {desc}"
        pd.font.size = Pt(9)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_after = Pt(6)

    # =========================================================================
    # SLIDE 16: Phone-First Experience: Instant Mobile QR Bridge
    # =========================================================================
    s16 = setup_slide(16)
    add_header(s16, "13. Phone-First Experience: Instant Mobile QR Bridge", "Turning any smartphone into an enterprise hardware scanner with zero app installation")

    add_framed_image(s16, assets["phone_qr"], 0.70, 1.65, 5.80, 3.45, "Dynamic QR Bridge: Instant Local LAN Connection for iQOO / Android Phones")

    tb_qr_t = s16.shapes.add_textbox(Inches(0.70), Inches(5.25), Inches(5.80), Inches(1.40))
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

    add_framed_image(s16, assets["scan_match"], 6.85, 1.65, 5.80, 3.45, "Live Mobile Scanner: Sub-200ms Recognition & Passport Matching")

    tb_sm_t = s16.shapes.add_textbox(Inches(6.85), Inches(5.25), Inches(5.80), Inches(1.40))
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
    # SLIDE 17: Bill Intelligence: Transparent Cost Explanations
    # =========================================================================
    s17 = setup_slide(17)
    add_header(s17, "14. Bill Intelligence: Transparent Cost Explanations", "Deconstructing utility and service bills into plain-language financial insights")

    add_card(s17, 0.70, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s17, 0.90, 1.82, 5.40, 0.35, "₹4,872 ELECTRICITY BILL BREAKDOWN", BLUE_ACCENT, WHITE, 10.5)

    tb_bill_t = s17.shapes.add_textbox(Inches(0.90), Inches(2.35), Inches(5.40), Inches(4.10))
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

    add_card(s17, 6.85, 1.65, 5.80, 5.00, WHITE, BORDER_LIGHT, 1)
    add_pill(s17, 7.05, 1.82, 5.40, 0.35, "AI PLAIN-LANGUAGE EXPLANATION", GOLD, NAVY_DARK, 10.5)

    q_box = add_card(s17, 7.05, 2.35, 5.40, 1.30, GOLD_LIGHT, GOLD, 1.5)
    tb_q = s17.shapes.add_textbox(Inches(7.20), Inches(2.45), Inches(5.10), Inches(1.10))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    p_q = tf_q.paragraphs[0]
    p_q.text = "“Your bill increased 31% primarily due to higher seasonal AC usage (+₹1,730) and an avoidable ₹300 late fee.”"
    p_q.font.size = Pt(12)
    p_q.font.bold = True
    p_q.font.color.rgb = TEXT_DARK

    tb_b_exp = s17.shapes.add_textbox(Inches(7.05), Inches(3.80), Inches(5.40), Inches(2.70))
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
    # SLIDE 18: Offline & Privacy Mode on Snapdragon NPU (NEW SLIDE)
    # =========================================================================
    s18 = setup_slide(18)
    add_header(s18, "15. Offline & Privacy Mode: Snapdragon NPU Edge AI", "Demonstrating zero cloud leakage: Complete end-to-end processing directly on the device")

    # Pipeline Box
    pipe_card = add_card(s18, 0.70, 1.60, 11.95, 1.80, NAVY_DARK, GREEN_TEAL, 1.5)
    tb_npu = s18.shapes.add_textbox(Inches(0.85), Inches(1.70), Inches(11.65), Inches(1.60))
    tf_npu = tb_npu.text_frame
    tf_npu.word_wrap = True

    p_np1 = tf_npu.paragraphs[0]
    p_np1.text = "OFFLINE AIRPLANE MODE ON SNAPDRAGON NPU"
    p_np1.font.bold = True
    p_np1.font.size = Pt(13)
    p_np1.font.color.rgb = GOLD
    p_np1.alignment = PP_ALIGN.CENTER

    p_np2 = tf_npu.add_paragraph()
    p_np2.text = "Camera  →  Local OCR  →  Local Extraction  →  Local DB Vault  →  Local SLM  →  Verified Answer\n[ 0ms Network Latency  •  Zero Cloud Upload  •  100% On-Device Private Processing ]"
    p_np2.font.name = "Consolas"
    p_np2.font.size = Pt(12)
    p_np2.font.color.rgb = WHITE
    p_np2.alignment = PP_ALIGN.CENTER

    # 3 Strategic Deep Dives
    add_bullet_card(s18, 0.70, 3.60, 3.80, 3.05, "1. AIRPLANE MODE DEMO", GREEN_TEAL, [
        "Demonstrated live during judging: Airplane Mode enabled.",
        "Scan paper invoice & snap appliance photo with zero internet.",
        "Generates full DPP passport in 180ms entirely on local hardware.",
        "Judges can verify: zero network packets sent outside.",
    ], "Real Edge Independence")

    add_bullet_card(s18, 4.77, 3.60, 3.80, 3.05, "2. SENSITIVE DATA SHIELD", BLUE_ACCENT, [
        "Invoices contain bank info, addresses, and customer names.",
        "Cloud LLM upload risks catastrophic privacy exposure.",
        "Verid keeps confidential household data locked inside local SQLite.",
        "Complies with European GDPR and ISO 27001 data residency.",
    ], "Total Household Privacy")

    add_bullet_card(s18, 8.85, 3.60, 3.80, 3.05, "3. SNAPDRAGON NPU BOOST", GOLD, [
        "Optimized for Snapdragon NPU hardware acceleration.",
        "Int8 quantized YOLO & ONNX OCR run at 4x speed and 1/3 power.",
        "Sub-100ms inference without draining smartphone battery.",
        "Hardware-level security enclave protects passport encryption keys.",
    ], "Qualcomm Snapdragon Ready")

    # =========================================================================
    # SLIDE 19: The 5-Layer Household Intelligence Architecture (NEW SLIDE)
    # =========================================================================
    s19 = setup_slide(19)
    add_header(s19, "16. Master Architecture: The 5-Layer Household Stack", "A full-stack operating hierarchy connecting edge silicon to conversational reasoning")

    layers = [
        ("LAYER 5: AI COPILOT", GOLD, [
            "“Ask My House” conversational interface",
            "Point-and-Ask AR Camera Mode",
            "Household Health Attention Center",
            "1-Tap Warranty Claim Pack generator",
        ], "User Interaction & Experience"),

        ("LAYER 4: RAG & REASONING", GREEN_TEAL, [
            "Trust & Evidence Layer (Answer/Why/Source)",
            "Predictive Maintenance Event Engine",
            "AI Manual Assistant & Document Grounding",
            "Bill Intelligence cost breakdown engine",
        ], "Intelligence & Logic Layer"),

        ("LAYER 3: HOUSEHOLD GRAPH", BLUE_ACCENT, [
            "Semantic Product Graph topology",
            "Appliance entity linking & cross-indexing",
            "Consumable & replacement parts catalog",
            "Temporal & seasonal event triggers",
        ], "Knowledge & Graph Layer"),

        ("LAYER 2: MEMORY & REGISTRY", GOLD, [
            "Deterministic SHA-256 Hasher",
            "SQLite Local Encrypted Vault",
            "EU Ecodesign DPP Schema Validator",
            "Immutable audit timeline & certificate seal",
        ], "Storage & Integrity Vault"),

        ("LAYER 1: SILICON & SENSORS", BLUE_ACCENT, [
            "Smartphone Camera + Microphone",
            "Snapdragon NPU Hardware Acceleration",
            "Fine-Tuned Custom YOLOv8 (~80ms)",
            "RapidOCR Offline Engine (~120ms)",
        ], "Edge Perception Layer"),
    ]
    lw = 2.25
    lgap = 0.18
    lx = 0.70
    for title, col, pts, sub in layers:
        add_card(s19, lx, 1.65, lw, 3.75, WHITE, BORDER_LIGHT, 1)
        add_pill(s19, lx + 0.10, 1.80, lw - 0.20, 0.35, title, col, WHITE, 9)

        tb_l = s19.shapes.add_textbox(Inches(lx + 0.10), Inches(2.25), Inches(lw - 0.20), Inches(3.05))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True

        p_sub = tf_l.paragraphs[0]
        p_sub.text = sub
        p_sub.font.bold = True
        p_sub.font.size = Pt(10)
        p_sub.font.color.rgb = TEXT_DARK
        p_sub.space_after = Pt(4)

        for pt in pts:
            p = tf_l.add_paragraph()
            p.text = f"• {pt}"
            p.font.size = Pt(8.5)
            p.font.color.rgb = TEXT_MUTED
            p.space_after = Pt(2)

        lx += lw + lgap

    # Architecture Bridge Card (Smartphone Edge + PC/Laptop Bridge)
    bridge_card = add_card(s19, 0.70, 5.55, 11.95, 1.25, NAVY_CARD, GOLD, 1.5)
    
    add_pill(s19, 0.90, 5.70, 3.40, 0.35, "MOBILE EDGE: SENSORS & NPU", BLUE_ACCENT, WHITE, 9.5)
    add_pill(s19, 4.55, 5.70, 4.25, 0.35, "◄── Dynamic LAN QR Bridge (192.168.1.4) ──►", NAVY_LIGHT, GOLD, 9)
    add_pill(s19, 9.05, 5.70, 3.40, 0.35, "COMPUTE BRIDGE: REGISTRY VAULT", GREEN_TEAL, WHITE, 9.5)
    
    tb_br = s19.shapes.add_textbox(Inches(0.90), Inches(6.12), Inches(11.55), Inches(0.60))
    tf_br = tb_br.text_frame
    tf_br.word_wrap = True
    p_br = tf_br.paragraphs[0]
    p_br.text = "System Philosophy: The smartphone is the active sensory edge in daily life (camera vision, voice, on-device NPU); the PC / laptop acts as the high-throughput local compute engine and tamper-proof registry bridge."
    p_br.font.size = Pt(9.5)
    p_br.font.color.rgb = RGBColor(0xD2, 0xDC, 0xE6)
    p_br.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 20: Traditional Storage vs. Verid Household OS
    # =========================================================================
    s20 = setup_slide(20)
    add_header(s20, "17. Why We Win: Traditional Storage vs. Verid Household OS", "Comparing passive file folders with an active, interconnected Household Intelligence System")

    table_card = add_card(s20, 0.70, 1.65, 11.95, 5.00, WHITE, BORDER_LIGHT, 1)

    add_pill(s20, 0.90, 1.80, 2.50, 0.38, "DIMENSION", NAVY_DARK, WHITE, 10.5)
    add_pill(s20, 3.55, 1.80, 4.30, 0.38, "TRADITIONAL WARRANTY STORAGE", RGBColor(0x94, 0xA3, 0xB8), WHITE, 10.5)
    add_pill(s20, 8.00, 1.80, 4.45, 0.38, "VERID HOUSEHOLD INTELLIGENCE OS", GOLD, NAVY_DARK, 10.5)

    comp_rows = [
        ("Evidence Intake", "Manual PDF upload to Google Drive / folder", "Dual-Anchor: Commercial document + Real physical hardware photo"),
        ("Physical Proof", "NONE (Zero validation of actual hardware possession)", "Real-time Fine-Tuned Custom YOLOv8 computer vision detection"),
        ("Knowledge Model", "Disconnected flat files in folder hierarchy", "Interconnected Household Product Graph with 12 entity nodes"),
        ("Real-Time Interaction", "Manual folder search through hundreds of files", "Point-and-Ask Camera AR HUD + natural voice querying"),
        ("Lifecycle Health", "Passive calendar reminder (often missed or ignored)", "Household Health Attention Center (Red/Amber/Green alerts)"),
        ("Claim Filing", "Spend 3 hours hunting invoices during breakdowns", "1-Tap Warranty Claim Pack formatted for vendor claim desks"),
        ("Privacy Architecture", "Uploads sensitive receipts to third-party clouds", "100% On-Device Snapdragon NPU execution in Airplane Mode"),
    ]
    ry = 2.30
    for dim, trad, verid in comp_rows:
        tb_r = s20.shapes.add_textbox(Inches(0.90), Inches(ry), Inches(11.55), Inches(0.60))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True

        p = tf_r.paragraphs[0]
        p.text = f"{dim.ljust(18)}  |  {trad[:42].ljust(45)}  |  ✓ {verid}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK

        hl = s20.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.90), Inches(ry + 0.60), Inches(11.55), Inches(0.01))
        hl.fill.solid()
        hl.fill.fore_color.rgb = RGBColor(0xEE, 0xE8, 0xDA)
        hl.line.fill.background()

        ry += 0.62

    # =========================================================================
    # SLIDE 21: Live Demo Story: 3-Minute Judge Walkthrough
    # =========================================================================
    s21 = setup_slide(21)
    add_header(s21, "18. Live Demo Story: The 3-Minute Winning Walkthrough", "A crisp, reproducible demonstration flow built specifically for hackathon judges")

    demo_steps = [
        ("01  OVERVIEW & HEALTH", "Minute 0:00 – 0:45", BLUE_ACCENT, [
            "Open Overview Dashboard.",
            "Inspect live statistics & Trust Center AI model health.",
            "Show Household Health Attention Center: Red (AC warranty 21d), Amber (Washing Machine maintenance).",
        ]),
        ("02  POINT-AND-ASK AR", "Minute 0:45 – 1:30", GOLD, [
            "Point mobile phone camera at physical washing machine.",
            "Instant AR HUD card pops up in <80ms via YOLO.",
            "Ask naturally: 'How old is this?' → Voice responds instantly from local memory.",
        ]),
        ("03  1-TAP DUAL INTAKE", "Minute 1:30 – 2:15", GREEN_TEAL, [
            "Tap 1-Click Electrolux Demo Preset.",
            "RapidOCR extracts Serial & Date in 120ms with zero hallucination.",
            "Custom YOLO detects appliance with 95% confidence score.",
        ]),
        ("04  CLAIM PACK & PRIVACY", "Minute 2:15 – 3:00", BLUE_ACCENT, [
            "Open passport → Click 'Generate 1-Tap Claim Pack' ready for official vendor filing.",
            "Demonstrate Airplane Mode test: 100% on-device NPU processing without internet!",
        ]),
    ]
    dw = 2.85
    dgap = 0.18
    dx = 0.70
    for title, timing, color, points in demo_steps:
        add_card(s21, dx, 1.65, dw, 5.00, WHITE, BORDER_LIGHT, 1)
        add_pill(s21, dx + 0.15, 1.82, dw - 0.30, 0.35, title, color, WHITE, 9.5)

        tb_d = s21.shapes.add_textbox(Inches(dx + 0.15), Inches(2.28), Inches(dw - 0.30), Inches(4.20))
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
    # SLIDE 22: Conclusion (Dark Theme)
    # =========================================================================
    s22 = setup_slide(22, is_dark=True)
    add_pill(s22, 0.88, 0.85, 3.80, 0.36, "iQOO HACKATHON 2026 • CONCLUSION", GOLD, NAVY_DARK, 10.5)

    tb22 = s22.shapes.add_textbox(Inches(0.85), Inches(1.35), Inches(11.50), Inches(0.85))
    tf22 = tb22.text_frame
    p22 = tf22.paragraphs[0]
    p22.text = "Verid: Household Intelligence OS"
    p22.font.name = FONT_HEADING
    p22.font.size = Pt(36)
    p22.font.bold = True
    p22.font.color.rgb = WHITE

    tb22_sub = s22.shapes.add_textbox(Inches(0.88), Inches(2.25), Inches(11.50), Inches(0.45))
    p22_sub = tb22_sub.text_frame.paragraphs[0]
    p22_sub.text = "“We Built It. We Proved It. It Scaled to Every Household.”"
    p22_sub.font.size = Pt(18)
    p22_sub.font.bold = True
    p22_sub.font.color.rgb = GOLD

    pillars = [
        ("1. WE BUILT IT", BLUE_ACCENT, [
            "Complete working full-stack system running live locally.",
            "Vite 7 + React 19 web frontend with instant Phone QR scanner.",
            "FastAPI microservice executing Custom YOLOv8 and RapidOCR.",
            "Zero placeholder mockups: real working code on local hardware.",
        ]),
        ("2. WE PROVED IT", GREEN_TEAL, [
            "98.10% mAP@50 and 99.29% precision validation results.",
            "Household Product Graph connecting 12 intelligent entity nodes.",
            "Point-and-Ask Camera AR mode with instant hardware identification.",
            "Cryptographic SHA-256 deterministic sealing of passport records.",
        ]),
        ("3. IT SCALES BIGGER", GOLD, [
            "Household Health Center eliminates costly missed warranties.",
            "1-Tap Warranty Claim Pack makes vendor claims seamless.",
            "Snapdragon NPU on-device engine enables 100% private offline AI.",
            "Transforms scattered documents into a true Household OS.",
        ]),
    ]
    pw = 3.75
    pgap = 0.35
    px = 0.88
    for title, color, points in pillars:
        add_card(s22, px, 2.95, pw, 3.10, NAVY_CARD, color, 1.5)
        add_pill(s22, px + 0.15, 3.10, pw - 0.30, 0.35, title, color, WHITE, 11)

        tb_p = s22.shapes.add_textbox(Inches(px + 0.15), Inches(3.60), Inches(pw - 0.30), Inches(2.30))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True

        for i, pt in enumerate(points):
            p = tf_p.paragraphs[0] if i == 0 else tf_p.add_paragraph()
            p.text = f"✓  {pt}"
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_LIGHT
            p.space_after = Pt(4)

        px += pw + pgap

    tb_team = s22.shapes.add_textbox(Inches(0.88), Inches(6.20), Inches(11.50), Inches(0.50))
    p_team = tb_team.text_frame.paragraphs[0]
    p_team.text = "Team Verid • GitHub Repository: https://github.com/ATS-AI-6278/IQ-Hackathon • Ready for Judging Q&A"
    p_team.font.bold = True
    p_team.font.size = Pt(12)
    p_team.font.color.rgb = GOLD

    output_path = "Smart_Product_Passport_Advanced.pptx"
    prs.save(output_path)
    print(f"Presentation successfully generated and saved to {output_path} ({TOTAL_SLIDES} slides).")

if __name__ == "__main__":
    build_presentation()
