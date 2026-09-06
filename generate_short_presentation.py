"""Short Verid pitch deck: unique slides only, no repeated feature dumps."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from lxml import etree

NAVY_DARK = RGBColor(0x0F, 0x1B, 0x2D)
NAVY_CARD = RGBColor(0x19, 0x2B, 0x44)
CREAM_BG = RGBColor(0xF7, 0xF4, 0xEC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GOLD = RGBColor(0xCA, 0xA0, 0x49)
GOLD_LIGHT = RGBColor(0xFA, 0xF3, 0xE0)
BLUE_ACCENT = RGBColor(0x2A, 0x5B, 0x8C)
BLUE_LIGHT = RGBColor(0xEE, 0xF4, 0xFB)
GREEN_TEAL = RGBColor(0x1F, 0x7A, 0x63)
GREEN_LIGHT = RGBColor(0xEB, 0xF6, 0xF2)
RED_ACCENT = RGBColor(0xDC, 0x26, 0x26)
ORANGE_WARN = RGBColor(0xEA, 0x58, 0x0C)
TEXT_DARK = RGBColor(0x0F, 0x1B, 0x2D)
TEXT_MUTED = RGBColor(0x55, 0x65, 0x75)
TEXT_LIGHT = RGBColor(0xF1, 0xF5, 0xF9)
BORDER_LIGHT = RGBColor(0xDF, 0xD8, 0xC8)

FONT_HEADING = "Calibri"
FONT_BODY = "Calibri"
TOTAL_SLIDES = 10

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "presentation_assets")


def set_run_font(run, name, size, bold=False, color=TEXT_DARK):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    # East Asian / latin fallback so Calibri actually applies in PowerPoint
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}%s" % tag.split(":")[1])
        if el is None:
            el = etree.SubElement(rPr, "{http://schemas.openxmlformats.org/drawingml/2006/main}%s" % tag.split(":")[1])
        el.set("typeface", name)


def p_text(tf, text, size, bold=False, color=TEXT_DARK, align=PP_ALIGN.LEFT, space_after=4, first=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    run = p.add_run()
    run.text = text
    set_run_font(run, FONT_BODY, size, bold, color)
    return p


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.500)
    blank = prs.slide_layouts[6]

    def img(name):
        path = os.path.join(ASSETS, name)
        return path if os.path.exists(path) else None

    assets = {
        "doc": img("01_input_warranty_document.png"),
        "photo": img("02_input_physical_product_photo.png"),
        "ocr_yolo": img("06_review_ocr_and_yolo_detection.png"),
        "confusion": img("08_model_confusion_matrix.png"),
        "curves": img("09_model_training_metrics_curves.png"),
        "passport": img("07_passport_minted_verified.png"),
        "cert": img("12_official_dpp_certificate_seal.png"),
        "graph": img("15_household_product_graph.jpg"),
        "point_ask": img("13_point_and_ask_camera_ar.jpg"),
        "health": img("14_household_health_attention_center.jpg"),
        "phone_qr": img("11_phone_connect_qr_bridge.png"),
        "scan": img("10_live_scanner_match_result.png"),
    }

    def setup(n, dark=False):
        slide = prs.slides.add_slide(blank)
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.500))
        bg.fill.solid()
        bg.fill.fore_color.rgb = NAVY_DARK if dark else CREAM_BG
        bg.line.fill.background()
        div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(7.03), Inches(12.00), Inches(0.015))
        div.fill.solid()
        div.fill.fore_color.rgb = GOLD
        div.line.fill.background()
        tb = slide.shapes.add_textbox(Inches(0.65), Inches(7.06), Inches(8.5), Inches(0.28))
        p = tb.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = "Verid — Household Intelligence OS  ·  iQOO Hackathon 2026"
        set_run_font(r, FONT_BODY, 10, False, GOLD if dark else TEXT_MUTED)
        tb2 = slide.shapes.add_textbox(Inches(11.55), Inches(7.06), Inches(1.15), Inches(0.28))
        p2 = tb2.text_frame.paragraphs[0]
        p2.alignment = PP_ALIGN.RIGHT
        r2 = p2.add_run()
        r2.text = f"{n:02d} / {TOTAL_SLIDES:02d}"
        set_run_font(r2, FONT_BODY, 10, True, GOLD)
        return slide

    def header(slide, title, subtitle):
        tb = slide.shapes.add_textbox(Inches(0.65), Inches(0.32), Inches(12.05), Inches(0.50))
        p = tb.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = title
        set_run_font(r, FONT_HEADING, 24, True, TEXT_DARK)
        tb2 = slide.shapes.add_textbox(Inches(0.65), Inches(0.82), Inches(12.05), Inches(0.36))
        p2 = tb2.text_frame.paragraphs[0]
        r2 = p2.add_run()
        r2.text = subtitle
        set_run_font(r2, FONT_BODY, 13, False, TEXT_MUTED)

    def card(slide, l, t, w, h, bg=WHITE, border=BORDER_LIGHT, bw=1):
        sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
        sh.fill.solid()
        sh.fill.fore_color.rgb = bg
        sh.line.color.rgb = border
        sh.line.width = Pt(bw)
        return sh

    def pill(slide, l, t, w, h, text, bg, fg, size=10):
        sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
        sh.fill.solid()
        sh.fill.fore_color.rgb = bg
        sh.line.fill.background()
        tf = sh.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = text
        set_run_font(r, FONT_BODY, size, True, fg)
        return sh

    def framed(slide, path, l, t, w, h, caption=""):
        card(slide, l, t, w, h, WHITE, BORDER_LIGHT, 1)
        cap_h = 0.26 if caption else 0.0
        pad = 0.07
        if path:
            slide.shapes.add_picture(path, Inches(l + pad), Inches(t + pad), Inches(w - pad * 2), Inches(h - pad * 2 - cap_h))
        if caption:
            tb = slide.shapes.add_textbox(Inches(l + pad), Inches(t + h - cap_h - 0.02), Inches(w - pad * 2), Inches(cap_h))
            p = tb.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = caption
            set_run_font(r, FONT_BODY, 9, True, BLUE_ACCENT)

    def bullets(tf, items, size=11, color=TEXT_MUTED, first=True):
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if (first and i == 0) else tf.add_paragraph()
            p.space_after = Pt(5)
            r = p.add_run()
            r.text = "•  " + item
            set_run_font(r, FONT_BODY, size, False, color)

    # -------------------------------------------------------------------------
    # 1 Cover
    # -------------------------------------------------------------------------
    s = setup(1, True)
    pill(s, 0.85, 0.78, 3.55, 0.34, "iQOO HACKATHON 2026  ·  AI TRACK", GOLD, NAVY_DARK, 11)
    tb = s.shapes.add_textbox(Inches(0.85), Inches(1.28), Inches(7.6), Inches(0.85))
    p = tb.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "Household Intelligence OS"
    set_run_font(r, FONT_HEADING, 36, True, WHITE)
    tb = s.shapes.add_textbox(Inches(0.85), Inches(2.12), Inches(7.6), Inches(0.50))
    p = tb.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "“Your phone remembers everything you own.”"
    set_run_font(r, FONT_HEADING, 18, True, GOLD)
    tb = s.shapes.add_textbox(Inches(0.85), Inches(2.72), Inches(7.5), Inches(1.15))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Verid turns invoices, warranties, and appliance photos into a living Household Product Graph — then answers questions from that memory, on-device."
    set_run_font(r, FONT_BODY, 14, False, RGBColor(0xD2, 0xDC, 0xE6))

    labels = [
        ("Custom YOLO  98.1% mAP", BLUE_ACCENT),
        ("RapidOCR  zero fabrication", GREEN_TEAL),
        ("Product Graph + Ask My House", GOLD),
        ("Snapdragon NPU  offline", BLUE_ACCENT),
    ]
    x = 0.85
    for text, col in labels:
        pill(s, x, 4.10, 1.85, 0.32, text, col, WHITE, 9)
        x += 1.95

    tb = s.shapes.add_textbox(Inches(0.85), Inches(4.60), Inches(7.5), Inches(1.90))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "What judges will see"
    set_run_font(r, FONT_BODY, 12, True, GOLD)
    bullets(tf, [
        "Dual evidence: commercial PDF + real hardware photo",
        "Point-and-ask camera + phone QR (no app install)",
        "Health Center alerts + 1-tap warranty claim pack",
        "Airplane-mode pipeline: camera → OCR → vault → answer",
    ], 13, RGBColor(0xCB, 0xD5, 0xE1), first=False)

    card(s, 8.70, 1.10, 3.85, 5.15, NAVY_CARD, GOLD, 2)
    tb = s.shapes.add_textbox(Inches(8.95), Inches(1.30), Inches(3.40), Inches(0.40))
    p = tb.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "VERID HOUSEHOLD BRAIN"
    set_run_font(r, FONT_BODY, 13, True, GOLD)
    lines = [
        ("Product", "Electrolux EcoCare 900"),
        ("Serial", "SN-WM900-2026-8842"),
        ("Warranty", "Active · 187 days left"),
        ("Repair index", "8.6 / 10  ·  Eco A++"),
        ("Seal", "SHA-256 invoice + photo"),
        ("Privacy", "100% local vault"),
    ]
    tb = s.shapes.add_textbox(Inches(8.95), Inches(1.80), Inches(3.40), Inches(2.70))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, (k, v) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(6)
        r = p.add_run()
        r.text = f"{k}:  {v}"
        set_run_font(r, FONT_BODY, 12, False, WHITE if i == 0 else RGBColor(0xCB, 0xD5, 0xE1))
    pill(s, 8.95, 4.70, 3.35, 0.32, "Point-and-Ask camera ready", GREEN_TEAL, WHITE, 10)
    pill(s, 8.95, 5.12, 3.35, 0.32, "Attention Center active", RED_ACCENT, WHITE, 10)
    pill(s, 8.95, 5.54, 3.35, 0.32, "EU Ecodesign DPP", GOLD, NAVY_DARK, 10)

    # -------------------------------------------------------------------------
    # 2 Problem
    # -------------------------------------------------------------------------
    s = setup(2)
    header(s, "The problem: ownership has no memory", "Documents exist. They are not connected to the appliance, the room, or time.")
    cols = [
        (BLUE_ACCENT, "Scattered proof", "Serials hide on hardware. Receipts live in drawers. Manuals stay unread. A breakdown becomes a paper hunt."),
        (GOLD, "Warranties die quietly", "Most coverage lapses with no reminder. Claims fail without invoice + serial. Cost shows up only after the repair bill."),
        (GREEN_TEAL, "Bills and upkeep are opaque", "Filters and AC service get skipped. A +31% electricity spike has no product attribution. Nothing links hardware to running cost."),
    ]
    x = 0.65
    for col, title, body in cols:
        card(s, x, 1.40, 3.90, 4.55, WHITE, BORDER_LIGHT, 1)
        pill(s, x + 0.22, 1.60, 3.46, 0.38, title.upper(), col, WHITE, 12)
        tb = s.shapes.add_textbox(Inches(x + 0.28), Inches(2.20), Inches(3.34), Inches(3.40))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = body
        set_run_font(r, FONT_BODY, 15, False, TEXT_DARK)
        x += 4.10
    card(s, 0.65, 6.10, 12.05, 0.70, GOLD_LIGHT, GOLD, 1.5)
    tb = s.shapes.add_textbox(Inches(0.85), Inches(6.20), Inches(11.65), Inches(0.50))
    p = tb.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "The gap is not missing files — it is a system that cannot anchor, connect, and reason over them."
    set_run_font(r, FONT_BODY, 14, True, TEXT_DARK)

    # -------------------------------------------------------------------------
    # 3 Shift
    # -------------------------------------------------------------------------
    s = setup(3)
    header(s, "The shift: a Household Intelligence OS", "Products + documents + events become one local memory — then a grounded assistant.")
    card(s, 0.65, 1.35, 12.05, 2.35, NAVY_DARK, GOLD, 1.5)
    tb = s.shapes.add_textbox(Inches(0.90), Inches(1.50), Inches(11.55), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Physical products   ·   Commercial docs   ·   Lifecycle events"
    set_run_font(r, FONT_BODY, 16, True, GOLD)
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "↓"
    set_run_font(r, FONT_BODY, 14, False, WHITE)
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Household Product Graph  (local encrypted vault)"
    set_run_font(r, FONT_BODY, 16, True, WHITE)
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "↓     Ask My House  ·  Point-and-Ask camera  ·  Health Center"
    set_run_font(r, FONT_BODY, 14, False, RGBColor(0xD2, 0xDC, 0xE6))

    three = [
        (BLUE_ACCENT, "Connected entity", "Each appliance is a node: serial, invoice, warranty clock, manual, parts, service log — not a PDF in a folder."),
        (GOLD, "Time-aware", "Purchase → install → service interval → filter life → expiry alert. Seasonal advice (pre-summer AC) sits on the same graph."),
        (GREEN_TEAL, "Private by default", "Invoices and room photos stay on the phone / PC vault. Airplane-mode path: camera → OCR → SQLite → local SLM."),
    ]
    x = 0.65
    for col, title, body in three:
        card(s, x, 3.90, 3.90, 2.80, WHITE, BORDER_LIGHT, 1)
        pill(s, x + 0.20, 4.08, 3.50, 0.36, title.upper(), col, WHITE, 11)
        tb = s.shapes.add_textbox(Inches(x + 0.24), Inches(4.58), Inches(3.42), Inches(1.90))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = body
        set_run_font(r, FONT_BODY, 13, False, TEXT_MUTED)
        x += 4.10

    # -------------------------------------------------------------------------
    # 4 Pipeline (merged dual intake + OCR + YOLO)
    # -------------------------------------------------------------------------
    s = setup(4)
    header(s, "How a passport is minted", "One flow: paper + photo → RapidOCR + custom YOLO → human review → cryptographic DPP.")
    framed(s, assets["doc"], 0.65, 1.32, 4.05, 2.55, "Commercial anchor")
    framed(s, assets["photo"], 4.85, 1.32, 3.70, 2.55, "Hardware photo")
    card(s, 8.70, 1.32, 4.00, 2.55, WHITE, BORDER_LIGHT, 1)
    pill(s, 8.90, 1.48, 3.60, 0.32, "EXTRACTED FIELDS", BLUE_ACCENT, WHITE, 10)
    tb = s.shapes.add_textbox(Inches(8.90), Inches(1.90), Inches(3.60), Inches(1.80))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate([
        "Electrolux EcoCare 900",
        "Model EWF9042R7WB",
        "Serial SN-WM900-2026-8842",
        "Purchase 12 Aug 2026  ·  2-year warranty",
        "YOLO class: washing machine",
    ]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(3)
        r = p.add_run()
        r.text = "•  " + line
        set_run_font(r, FONT_BODY, 12, False, TEXT_DARK)

    framed(s, assets["ocr_yolo"], 0.65, 4.02, 6.40, 2.70, "Review: OCR fields + vision match before mint")
    card(s, 7.20, 4.02, 5.50, 2.70, WHITE, BORDER_LIGHT, 1)
    tb = s.shapes.add_textbox(Inches(7.40), Inches(4.18), Inches(5.15), Inches(2.40))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Guards against fake or empty records"
    set_run_font(r, FONT_BODY, 13, True, TEXT_DARK)
    bullets(tf, [
        "RapidOCR ONNX ~120 ms, regex — no invented serials",
        "Custom YOLOv8: AC, washer, closet, purifier, cot",
        "Human confirm before SHA-256 seal of invoice + photo",
        "1-click demo presets for Electrolux / Haier / Aquasure",
    ], 12, TEXT_MUTED, first=False)

    # -------------------------------------------------------------------------
    # 5 ML proof
    # -------------------------------------------------------------------------
    s = setup(5)
    header(s, "Vision model: measured, not claimed", "YOLOv8n, 292 labeled images, 80/20 split, 25 epochs. Validation on 56 images.")
    metrics = [
        ("98.10%", "mAP@50", BLUE_ACCENT),
        ("99.29%", "Precision", GREEN_TEAL),
        ("98.57%", "Recall", GOLD),
        ("69–96 ms", "CPU latency", BLUE_ACCENT),
    ]
    x = 0.65
    for val, lab, col in metrics:
        card(s, x, 1.32, 2.95, 1.15, WHITE, BORDER_LIGHT, 1)
        tb = s.shapes.add_textbox(Inches(x + 0.08), Inches(1.38), Inches(2.79), Inches(1.02))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = val
        set_run_font(r, FONT_HEADING, 22, True, col)
        p = tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = lab
        set_run_font(r, FONT_BODY, 12, False, TEXT_MUTED)
        x += 3.15
    framed(s, assets["confusion"], 0.65, 2.62, 6.05, 4.05, "Confusion matrix — near-diagonal on 5 classes")
    framed(s, assets["curves"], 6.90, 2.62, 5.80, 4.05, "Train / val loss and mAP curves")

    # -------------------------------------------------------------------------
    # 6 DPP output
    # -------------------------------------------------------------------------
    s = setup(6)
    header(s, "Output: a verified Digital Product Passport", "EU Ecodesign-style certificate bound to physical proof — searchable, exportable, claim-ready.")
    framed(s, assets["passport"], 0.65, 1.32, 6.05, 5.35, "Minted passport in the registry")
    framed(s, assets["cert"], 6.90, 1.32, 5.80, 3.55, "Official Verid DPP seal")
    card(s, 6.90, 5.00, 5.80, 1.67, WHITE, BORDER_LIGHT, 1)
    tb = s.shapes.add_textbox(Inches(7.08), Inches(5.12), Inches(5.45), Inches(1.42))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "SHA-256 seals invoice + photo  ·  Repairability 8.6/10  ·  Eco A++  ·  PDF / print for vendor desks"
    set_run_font(r, FONT_BODY, 14, False, TEXT_DARK)

    # -------------------------------------------------------------------------
    # 7 Graph + Ask My House (merged graph, NLP, manuals)
    # -------------------------------------------------------------------------
    s = setup(7)
    header(s, "Household graph + Ask My House", "Questions hit the graph and indexed PDFs — not a generic LLM guessing dates.")
    framed(s, assets["graph"], 0.65, 1.32, 6.20, 5.35, "One appliance = identity, invoice, warranty, manual, parts, service")
    card(s, 7.05, 1.32, 5.65, 5.35, WHITE, BORDER_LIGHT, 1)
    pill(s, 7.25, 1.48, 5.25, 0.34, "GROUNDED Q & A", GOLD, NAVY_DARK, 11)
    qa = [
        ("When does the washer warranty expire?", "12 Aug 2028 · 187 days left"),
        ("What needs attention this month?", "Purifier filter 8% · AC flush overdue"),
        ("Where is the AC warranty card?", "Master Bedroom passport · original PDF"),
        ("How do I clean the drain filter?", "Manual §6.2 + compatible gasket part"),
        ("What did the tech replace last time?", "Mar 2026 drain pump gasket"),
    ]
    tb = s.shapes.add_textbox(Inches(7.25), Inches(1.95), Inches(5.25), Inches(4.50))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, (q, a) in enumerate(qa):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(2)
        r = p.add_run()
        r.text = q
        set_run_font(r, FONT_BODY, 12, True, TEXT_DARK)
        p = tf.add_paragraph()
        p.space_after = Pt(10)
        r = p.add_run()
        r.text = "→  " + a
        set_run_font(r, FONT_BODY, 12, False, GREEN_TEAL)

    # -------------------------------------------------------------------------
    # 8 Camera + Health + Claim (merged 11,12,13,16)
    # -------------------------------------------------------------------------
    s = setup(8)
    header(s, "Daily use: point, prioritize, claim", "Phone is the sensor. Health Center ranks risk. One tap builds a vendor claim pack.")
    framed(s, assets["point_ask"], 0.65, 1.28, 4.20, 3.35, "Point-and-Ask AR HUD")
    framed(s, assets["health"], 5.00, 1.28, 4.20, 3.35, "Red / amber / green attention")
    framed(s, assets["phone_qr"], 9.35, 1.28, 3.35, 3.35, "QR → live scan, no app")

    bits = [
        (BLUE_ACCENT, "Camera", "YOLO <80 ms. Overlay: name, warranty days, repair score. Voice: “Is this under warranty?”"),
        (ORANGE_WARN, "Health", "AC warranty 21 days · washer descaling due · purifier filter 8%. Healthy assets stay green."),
        (GOLD, "Claim pack", "Model, OCR serial, invoice PDF, warranty, service log, hardware photo, draft letter — one tap."),
    ]
    x = 0.65
    for col, title, body in bits:
        card(s, x, 4.78, 4.05, 1.92, WHITE, BORDER_LIGHT, 1)
        pill(s, x + 0.15, 4.92, 3.75, 0.30, title.upper(), col, WHITE if col != GOLD else NAVY_DARK, 11)
        tb = s.shapes.add_textbox(Inches(x + 0.18), Inches(5.30), Inches(3.70), Inches(1.25))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = body
        set_run_font(r, FONT_BODY, 12, False, TEXT_MUTED)
        x += 4.20

    # -------------------------------------------------------------------------
    # 9 Trust + offline + 5-layer stack (merged 15,18,19)
    # -------------------------------------------------------------------------
    s = setup(9)
    header(s, "Trust, privacy, and the stack", "Every answer cites a source. Sensitive docs never need a cloud LLM.")
    steps = [
        ("Answer", "Warranty ends 12 Aug 2028", BLUE_ACCENT, WHITE),
        ("Why", "Invoice page 2 states 2-year cover from purchase date", TEXT_DARK, BLUE_LIGHT),
        ("Source", "Tax invoice + warranty card  ·  page / line cited", GREEN_TEAL, GREEN_LIGHT),
        ("Confidence", "High OCR match + regex  ·  else: “could not verify”", GOLD, GOLD_LIGHT),
    ]
    y = 1.28
    for lab, txt, col, bg in steps:
        card(s, 0.65, y, 6.15, 1.18, bg, col, 1)
        tb = s.shapes.add_textbox(Inches(0.82), Inches(y + 0.10), Inches(5.82), Inches(0.98))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = lab.upper()
        set_run_font(r, FONT_BODY, 11, True, col)
        p = tf.add_paragraph()
        r = p.add_run()
        r.text = txt
        set_run_font(r, FONT_BODY, 13, False, TEXT_DARK)
        y += 1.28

    card(s, 7.00, 1.28, 5.70, 2.55, NAVY_DARK, GREEN_TEAL, 1.5)
    tb = s.shapes.add_textbox(Inches(7.18), Inches(1.42), Inches(5.35), Inches(2.25))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Airplane mode"
    set_run_font(r, FONT_BODY, 14, True, GOLD)
    p = tf.add_paragraph()
    r = p.add_run()
    r.text = "Camera → local OCR → extract → SQLite vault → local SLM → cited answer. Zero packets. Snapdragon NPU for YOLO / ONNX."
    set_run_font(r, FONT_BODY, 13, False, WHITE)

    layers = [
        ("5 Copilot", "Ask / camera / health / claim"),
        ("4 Reason", "RAG, trust, maintenance"),
        ("3 Graph", "Entities, parts, seasons"),
        ("2 Vault", "SHA-256, SQLite, DPP schema"),
        ("1 Silicon", "Camera, NPU, YOLO, RapidOCR"),
    ]
    x = 7.00
    for title, sub in layers:
        card(s, x, 4.00, 1.08, 2.68, WHITE, BORDER_LIGHT, 1)
        tb = s.shapes.add_textbox(Inches(x + 0.06), Inches(4.12), Inches(0.96), Inches(2.42))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = title
        set_run_font(r, FONT_BODY, 10, True, BLUE_ACCENT)
        p = tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = sub
        set_run_font(r, FONT_BODY, 10, False, TEXT_MUTED)
        x += 1.14

    # -------------------------------------------------------------------------
    # 10 Demo + close (merged 20,21,22 — comparison is 4 rows not 7)
    # -------------------------------------------------------------------------
    s = setup(10, True)
    pill(s, 0.85, 0.42, 3.20, 0.32, "LIVE DEMO  ·  3 MINUTES", GOLD, NAVY_DARK, 11)
    tb = s.shapes.add_textbox(Inches(0.85), Inches(0.82), Inches(11.6), Inches(0.48))
    p = tb.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "We built it. We measured it. Show the path, then stop."
    set_run_font(r, FONT_HEADING, 22, True, WHITE)

    demo = [
        ("0:00", "Dashboard + Health Center (red AC warranty, amber washer)"),
        ("0:45", "Point phone at washer → HUD + “How old is this?”"),
        ("1:30", "1-click Electrolux preset → OCR + YOLO review → mint"),
        ("2:15", "Claim pack + airplane-mode scan (no cloud)"),
    ]
    x = 0.85
    for t, body in demo:
        card(s, x, 1.45, 2.90, 2.05, NAVY_CARD, GOLD, 1)
        tb = s.shapes.add_textbox(Inches(x + 0.14), Inches(1.55), Inches(2.62), Inches(1.82))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = t
        set_run_font(r, FONT_BODY, 16, True, GOLD)
        p = tf.add_paragraph()
        r = p.add_run()
        r.text = body
        set_run_font(r, FONT_BODY, 12, False, TEXT_LIGHT)
        x += 3.05

    vs = [
        "Folders / Drive: PDFs with no hardware proof  →  Verid: invoice + photo + YOLO",
        "Search files:  →  Point-and-Ask + Ask My House on the product graph",
        "Missed expiry:  →  Health Center + 1-tap vendor claim pack",
        "Cloud chatbots:  →  On-device vault, cited confidence, honest fallback",
    ]
    tb = s.shapes.add_textbox(Inches(0.85), Inches(3.65), Inches(11.6), Inches(1.70))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Why this beats a Drive folder"
    set_run_font(r, FONT_BODY, 13, True, GOLD)
    for line in vs:
        p = tf.add_paragraph()
        p.space_after = Pt(3)
        r = p.add_run()
        r.text = "✓  " + line
        set_run_font(r, FONT_BODY, 13, False, TEXT_LIGHT)

    tb = s.shapes.add_textbox(Inches(0.85), Inches(5.50), Inches(11.6), Inches(1.20))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Team Verid  ·  working code (Vite + FastAPI + YOLOv8 + RapidOCR)  ·  github.com/ATS-AI-6278/IQ-Hackathon"
    set_run_font(r, FONT_BODY, 14, True, GOLD)
    p = tf.add_paragraph()
    r = p.add_run()
    r.text = "Ask My House. Point at the machine. File the claim. Stay offline."
    set_run_font(r, FONT_BODY, 14, False, RGBColor(0xD2, 0xDC, 0xE6))

    out_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Cursor Created")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Verid_Household_Intelligence_OS.pptx")
    prs.save(out_path)
    print(out_path)
    return out_path


if __name__ == "__main__":
    build()
