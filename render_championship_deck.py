"""Championship Verid pitch: pixel-identical PPTX + PDF (1920x1080)."""
from __future__ import annotations

import os
import shutil
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pptx import Presentation
from pptx.util import Inches, Emu
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

W, H = 1920, 1080
NAVY = (15, 27, 45)
NAVY2 = (19, 36, 58)
CREAM = (247, 244, 236)
WHITE = (255, 255, 255)
GOLD = (202, 160, 73)
GOLD2 = (232, 196, 112)
MUTED = (180, 190, 204)
MUTED_D = (86, 101, 117)
TEAL = (31, 122, 99)
BLUE = (42, 91, 140)
RED = (220, 38, 38)
ORANGE = (234, 88, 12)
INK = (15, 27, 45)

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = r"C:\Windows\Fonts"
AI = os.path.join(os.path.expanduser("~"), ".cursor", "projects", "c-Users-acer-Pictures-IQ", "assets")
SHOTS = os.path.join(ROOT, "presentation_assets")
OUT_PNG = os.path.join(ROOT, "championship_slides")
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop", "Cursor Created")


def font(name, size):
    path = os.path.join(FONTS, name)
    return ImageFont.truetype(path, size)


F_H1 = lambda s: font("georgiab.ttf", s)
F_H2 = lambda s: font("georgia.ttf", s)
F_B = lambda s: font("segoeui.ttf", s)
F_BB = lambda s: font("segoeuib.ttf", s)
F_L = lambda s: font("segoeuil.ttf", s)


def load(path, size=None, cover=False):
    im = Image.open(path).convert("RGB")
    if size is None:
        return im
    tw, th = size
    if cover:
        scale = max(tw / im.width, th / im.height)
        nw, nh = int(im.width * scale), int(im.height * scale)
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
        x = (nw - tw) // 2
        y = (nh - th) // 2
        return im.crop((x, y, x + tw, y + th))
    return im.resize((tw, th), Image.Resampling.LANCZOS)


def rounded(im, r=28):
    im = im.convert("RGBA")
    mask = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, im.size[0], im.size[1]), r, fill=255)
    im.putalpha(mask)
    return im


def paste_round(base, im, xy, size, r=24, shadow=True):
    im = load(im, size, cover=True) if isinstance(im, str) else im.resize(size, Image.Resampling.LANCZOS)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    im = rounded(im, r)
    if shadow:
        sh = Image.new("RGBA", (size[0] + 24, size[1] + 24), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((8, 10, size[0] + 8, size[1] + 10), r, fill=(0, 0, 0, 90))
        sh = sh.filter(ImageFilter.GaussianBlur(8))
        base.alpha_composite(sh, (xy[0] - 8, xy[1] - 6))
    base.alpha_composite(im, xy)


def rr(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def wrap(d, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_shadow(d, xy, text, fnt, fill, shadow=(0, 0, 0, 160)):
    x, y = xy
    d.text((x + 2, y + 2), text, font=fnt, fill=shadow)
    d.text((x, y), text, font=fnt, fill=fill)


def footer(d, n, total=12, light=False):
    col = (120, 130, 145) if light else (168, 176, 188)
    d.line((70, 1038, 1850, 1038), fill=GOLD, width=2)
    d.text((70, 1046), "Verid  ·  Household Intelligence OS  ·  iQOO Hackathon 2026", font=F_B(16), fill=col)
    label = f"{n:02d}  /  {total:02d}"
    d.text((1780, 1046), label, font=F_BB(16), fill=GOLD)


def pill(d, xy, w, h, text, bg, fg, fnt=None):
    fnt = fnt or F_BB(18)
    x, y = xy
    rr(d, (x, y, x + w, y + h), 18, fill=bg)
    tw = d.textlength(text, font=fnt)
    d.text((x + (w - tw) / 2, y + (h - fnt.size) / 2 - 2), text, font=fnt, fill=fg)


def canvas(color=NAVY):
    im = Image.new("RGBA", (W, H), color + (255,))
    return im, ImageDraw.Draw(im)


def bleed(path):
    im = load(path, (W, H), cover=True).convert("RGBA")
    return im, ImageDraw.Draw(im)


def veil(im, left=0, right=W, alpha=160, color=NAVY):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle((left, 0, right, H), fill=color + (alpha,))
    # soft right fade if partial
    if right < W:
        for i in range(80):
            a = int(alpha * (1 - i / 80))
            d.rectangle((right + i, 0, right + i + 1, H), fill=color + (a,))
    return Image.alpha_composite(im, overlay)


# ---------------------------------------------------------------------------
# SLIDES
# ---------------------------------------------------------------------------

def s01():
    im, _ = bleed(os.path.join(AI, "verid_cover_hero.png"))
    im = veil(im, 0, 980, 175)
    d = ImageDraw.Draw(im)
    pill(d, (80, 88), 430, 42, "iQOO HACKATHON 2026  ·  AI TRACK", GOLD, NAVY)
    text_shadow(d, (80, 170), "VERID", F_H1(92), GOLD2)
    d.text((80, 280), "Household Intelligence OS", font=F_H1(48), fill=WHITE)
    d.text((80, 360), "“Your phone remembers everything you own.”", font=F_H2(28), fill=GOLD)
    for i, line in enumerate(wrap(d, "Scattered invoices and appliance photos become a living household graph. Ask it. Point at it. Claim with it. All on-device.", F_B(26), 820)):
        d.text((80, 430 + i * 36), line, font=F_B(26), fill=(220, 228, 236))
    stats = [("98.1%", "mAP@50 YOLO"), ("99.3%", "Precision"), ("<100ms", "On-device"), ("0 cloud", "Airplane mode")]
    x = 80
    for val, lab in stats:
        rr(d, (x, 620, x + 200, 730), 16, fill=(12, 22, 36, 210), outline=GOLD, width=2)
        d.text((x + 18, 636), val, font=F_BB(32), fill=GOLD2)
        d.text((x + 18, 682), lab, font=F_B(16), fill=MUTED)
        x += 220
    d.text((80, 780), "Hardware proof  ·  Ask My House  ·  Health Center  ·  1-tap claim  ·  Snapdragon NPU", font=F_BB(20), fill=WHITE)
    footer(d, 1)
    return im


def s02():
    im, d = canvas(NAVY)
    # gold accent bar
    d.rectangle((0, 0, 14, H), fill=GOLD)
    pill(d, (80, 70), 260, 40, "THE BET", GOLD, NAVY)
    lines = wrap(d, "Drive stores files. Verid remembers the house.", F_H1(54), 1760)
    y = 150
    for line in lines:
        d.text((80, y), line, font=F_H1(54), fill=WHITE)
        y += 72
    d.text((80, 340), "Judges are not picking a PDF folder. They are picking the OS that owns the appliance after the receipt is forgotten.", font=F_B(26), fill=MUTED)
    cards = [
        (BLUE, "01", "Prove it is real", "Invoice + live photo. Custom YOLO. No paper-only fraud."),
        (TEAL, "02", "Ask it like a person", "Warranty, filter, last repair — cited from YOUR docs."),
        (GOLD, "03", "Act before it dies", "Health Center + 1-tap vendor claim pack."),
        ((90, 70, 40), "04", "Keep it private", "Airplane mode on Snapdragon NPU. iQOO’s home turf."),
    ]
    x = 80
    for col, num, title, body in cards:
        rr(d, (x, 430, x + 420, 960), 22, fill=NAVY2, outline=col, width=3)
        d.text((x + 28, 460), num, font=F_H1(36), fill=col)
        d.text((x + 28, 530), title, font=F_BB(26), fill=WHITE)
        by = 590
        for line in wrap(d, body, F_B(22), 360):
            d.text((x + 28, by), line, font=F_B(22), fill=MUTED)
            by += 32
        x += 450
    footer(d, 2)
    return im


def s03():
    im, d = canvas(CREAM)
    d.rectangle((0, 0, 14, H), fill=RED)
    d.text((80, 60), "Ownership has no memory", font=F_H1(44), fill=INK)
    d.text((80, 128), "The problem is not missing paper. It is that nothing is anchored, connected, or timed.", font=F_B(24), fill=MUTED_D)
    paste_round(im, os.path.join(AI, "verid_problem_chaos.png"), (980, 190), (860, 780), 28)
    pains = [
        (BLUE, "Scattered", "Serials fade. Receipts live in drawers. 80-page manuals stay unread. Breakdown = scavenger hunt."),
        (GOLD, "Silent expiry", "Most warranties lapse with no reminder. Claims fail without invoice + serial. You pay cash."),
        (TEAL, "Opaque cost", "Filters skip. AC never flushed. A +31% bill has no appliance to blame."),
    ]
    y = 200
    for col, t, b in pains:
        rr(d, (70, y, 940, y + 230), 20, fill=WHITE, outline=(223, 216, 200), width=2)
        d.rectangle((70, y, 86, y + 230), fill=col)
        d.text((110, y + 22), t, font=F_BB(26), fill=INK)
        by = y + 70
        for line in wrap(d, b, F_B(22), 780):
            d.text((110, by), line, font=F_B(22), fill=MUTED_D)
            by += 30
        y += 250
    footer(d, 3, light=True)
    return im


def s04():
    im, _ = bleed(os.path.join(AI, "verid_os_graph.png"))
    im = veil(im, 0, 860, 185)
    d = ImageDraw.Draw(im)
    pill(d, (70, 70), 340, 40, "THE SHIFT  ·  HOUSEHOLD OS", GOLD, NAVY)
    d.text((70, 140), "From dead files", font=F_H1(42), fill=WHITE)
    d.text((70, 198), "to a living graph.", font=F_H1(42), fill=GOLD2)
    flow = [
        "Products  ·  Documents  ·  Events",
        "↓",
        "Local Household Memory",
        "↓",
        "Ask  ·  Point  ·  Prioritize  ·  Claim",
    ]
    y = 300
    for i, t in enumerate(flow):
        col = GOLD2 if i % 2 == 0 else MUTED
        f = F_BB(24) if i % 2 == 0 else F_B(22)
        d.text((70, y), t, font=f, fill=col)
        y += 42
    bits = [
        "Every washer is a node: serial, invoice, warranty clock, manual, parts, service.",
        "Seasonal: pre-summer AC. Temporal: 187 days of cover left.",
        "Family-shared. Room-aware. Never a generic chatbot.",
    ]
    y = 560
    for b in bits:
        rr(d, (70, y, 820, y + 88), 14, fill=(12, 22, 36, 200), outline=GOLD, width=1)
        for j, line in enumerate(wrap(d, b, F_B(20), 700)[:2]):
            d.text((90, y + 16 + j * 28), line, font=F_B(20), fill=WHITE)
        y += 102
    footer(d, 4)
    return im


def s05():
    im, d = canvas(CREAM)
    d.text((70, 50), "Mint a passport: paper + physical proof", font=F_H1(38), fill=INK)
    d.text((70, 108), "RapidOCR (~120ms, regex — no invented serials)  +  custom YOLO  +  human review  +  SHA-256 seal", font=F_B(22), fill=MUTED_D)
    paste_round(im, os.path.join(SHOTS, "01_input_warranty_document.png"), (70, 170), (430, 360), 18)
    paste_round(im, os.path.join(SHOTS, "02_input_physical_product_photo.png"), (520, 170), (430, 360), 18)
    paste_round(im, os.path.join(SHOTS, "06_review_ocr_and_yolo_detection.png"), (970, 170), (880, 360), 18)
    d.text((70, 548), "Commercial anchor", font=F_BB(18), fill=BLUE)
    d.text((520, 548), "Hardware photo", font=F_BB(18), fill=TEAL)
    d.text((970, 548), "Review before mint (OCR fields + vision match)", font=F_BB(18), fill=GOLD)

    paste_round(im, os.path.join(SHOTS, "07_passport_minted_verified.png"), (70, 590), (600, 400), 18)
    paste_round(im, os.path.join(SHOTS, "12_official_dpp_certificate_seal.png"), (700, 590), (520, 400), 18)
    rr(d, (1250, 590, 1850, 990), 18, fill=WHITE, outline=GOLD, width=2)
    d.text((1280, 620), "What gets sealed", font=F_BB(24), fill=INK)
    items = [
        "Electrolux EcoCare 900",
        "Serial SN-WM900-2026-8842",
        "2-year warranty · 187d left",
        "Repair 8.6/10 · Eco A++",
        "SHA-256 of invoice + photo",
        "1-click Electrolux / Haier / Aquasure demos",
    ]
    y = 670
    for it in items:
        d.text((1280, y), "●  " + it, font=F_B(20), fill=MUTED_D)
        y += 46
    footer(d, 5, light=True)
    return im


def s06():
    im, d = canvas(CREAM)
    d.text((70, 48), "We trained the eyes. We published the score.", font=F_H1(38), fill=INK)
    d.text((70, 104), "YOLOv8n · 5 household classes · 292 images · 80/20 split · CPU 69–96 ms", font=F_B(22), fill=MUTED_D)
    metrics = [("98.10%", "mAP@50", BLUE), ("99.29%", "Precision", TEAL), ("98.57%", "Recall", GOLD), ("5 classes", "AC · washer · closet · purifier · cot", NAVY)]
    x = 70
    for val, lab, col in metrics:
        rr(d, (x, 160, x + 440, 300), 18, fill=WHITE, outline=col, width=3)
        d.text((x + 24, 178), val, font=F_H1(40), fill=col)
        d.text((x + 24, 242), lab, font=F_B(18), fill=MUTED_D)
        x += 460
    paste_round(im, os.path.join(SHOTS, "08_model_confusion_matrix.png"), (70, 340), (880, 650), 18)
    paste_round(im, os.path.join(SHOTS, "09_model_training_metrics_curves.png"), (980, 340), (870, 650), 18)
    footer(d, 6, light=True)
    return im


def s07():
    im, _ = bleed(os.path.join(AI, "verid_ask_house.png"))
    im = veil(im, 920, W, 200)
    # extra left dim
    left = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(left).rectangle((0, 0, 80, H), fill=NAVY + (80,))
    im = Image.alpha_composite(im, left)
    d = ImageDraw.Draw(im)
    pill(d, (980, 70), 320, 40, "ASK MY HOUSE", GOLD, NAVY)
    d.text((980, 130), "Grounded Q&A.", font=F_H1(40), fill=WHITE)
    d.text((980, 186), "Zero invented dates.", font=F_H1(32), fill=GOLD2)
    qa = [
        ("When does my washer warranty expire?", "12 Aug 2028 · 187 days left"),
        ("What needs attention this month?", "Purifier filter 8% · AC flush overdue"),
        ("Where is the AC warranty card?", "Master Bedroom passport · original PDF"),
        ("How do I clean the drain filter?", "Manual §6.2 + matching gasket part"),
        ("What did the tech replace last time?", "Mar 2026 · drain pump gasket"),
    ]
    y = 260
    for q, a in qa:
        rr(d, (980, y, 1850, y + 130), 14, fill=(12, 22, 36, 210), outline=(80, 90, 110), width=1)
        d.text((1004, y + 16), q, font=F_BB(18), fill=WHITE)
        d.text((1004, y + 70), "→  " + a, font=F_B(18), fill=GOLD2)
        y += 144
    footer(d, 7)
    return im


def s08():
    im, _ = bleed(os.path.join(AI, "verid_ar_hud.png"))
    im = veil(im, 0, 760, 170)
    d = ImageDraw.Draw(im)
    pill(d, (70, 70), 420, 40, "POINT-AND-ASK  ·  PHONE FIRST", GOLD, NAVY)
    d.text((70, 140), "Don’t search a folder.", font=F_H1(36), fill=WHITE)
    d.text((70, 196), "Point the camera.", font=F_H1(36), fill=GOLD2)
    bullets = [
        "YOLO lock in <80 ms",
        "HUD: name, warranty days, repair score",
        "Voice: “Is this under warranty?”",
        "QR bridge: scan, no app install",
        "Phone = sensor · PC = vault",
    ]
    y = 290
    for b in bullets:
        rr(d, (70, y, 700, y + 78), 14, fill=(12, 22, 36, 200), outline=GOLD, width=1)
        d.text((96, y + 22), "▸  " + b, font=F_B(22), fill=WHITE)
        y += 92
    footer(d, 8)
    return im


def s09():
    im, d = canvas(CREAM)
    d.text((70, 48), "Act: Health Center + 1-tap claim pack", font=F_H1(38), fill=INK)
    d.text((70, 104), "Red / amber / green before the breakdown. Vendor-ready dossier in one tap.", font=F_B(22), fill=MUTED_D)
    paste_round(im, os.path.join(AI, "verid_health_command.png"), (70, 160), (900, 520), 22)
    paste_round(im, os.path.join(AI, "verid_claim_pack.png"), (1000, 160), (850, 520), 22)
    rows = [
        (RED, "NOW", "Living Room AC — warranty 21 days. Extend or final inspect."),
        (ORANGE, "SOON", "Washer descaling due · Purifier carbon filter at 8% life."),
        (TEAL, "CLAIM", "Model + OCR serial + invoice PDF + service log + photo + letter."),
    ]
    x = 70
    for col, t, b in rows:
        rr(d, (x, 710, x + 590, 990), 18, fill=WHITE, outline=col, width=3)
        d.text((x + 24, 734), t, font=F_BB(22), fill=col)
        by = 790
        for line in wrap(d, b, F_B(20), 540):
            d.text((x + 24, by), line, font=F_B(20), fill=MUTED_D)
            by += 28
        x += 610
    footer(d, 9, light=True)
    return im


def s10():
    im, _ = bleed(os.path.join(AI, "verid_npu_offline.png"))
    im = veil(im, 0, 900, 180)
    d = ImageDraw.Draw(im)
    pill(d, (70, 70), 520, 40, "WHY iQOO  ·  SNAPDRAGON NPU", GOLD, NAVY)
    d.text((70, 140), "Airplane mode is the demo.", font=F_H1(40), fill=WHITE)
    d.text((70, 200), "Privacy is the product.", font=F_H1(32), fill=GOLD2)
    d.text((70, 280), "Camera → local OCR → extract → SQLite vault → local SLM → cited answer", font=F_BB(20), fill=WHITE)
    d.text((70, 320), "0 ms network  ·  0 cloud upload  ·  invoices never leave the house", font=F_B(20), fill=MUTED)
    cards = [
        ("Edge", "Int8 YOLO + ONNX OCR. Sub-100 ms. Battery-sane."),
        ("Shield", "Names, addresses, GST, bank lines stay in a local vault — not a chat API."),
        ("Bridge", "Phone sensors + NPU. Laptop registry. LAN QR, no Play Store."),
    ]
    y = 390
    for t, b in cards:
        rr(d, (70, y, 850, y + 160), 16, fill=(12, 22, 36, 210), outline=GOLD, width=2)
        d.text((96, y + 22), t, font=F_BB(24), fill=GOLD2)
        for j, line in enumerate(wrap(d, b, F_B(20), 710)):
            d.text((96, y + 68 + j * 28), line, font=F_B(20), fill=WHITE)
        y += 180
    footer(d, 10)
    return im


def s11():
    im, d = canvas(NAVY)
    d.rectangle((0, 0, 14, H), fill=GOLD)
    d.text((70, 50), "Why they should pick us", font=F_H1(44), fill=WHITE)
    d.text((70, 114), "Not more slides. A working Household OS on iQOO silicon.", font=F_B(24), fill=MUTED)
    rows = [
        ("Folders / Drive", "Verid Household OS"),
        ("PDF dump, no hardware proof", "Invoice + live photo + YOLO lock"),
        ("Search filenames", "Point-and-Ask + Ask My House"),
        ("Calendar reminder you ignore", "Health Center red / amber / green"),
        ("3-hour claim scavenger hunt", "1-tap vendor claim pack"),
        ("Cloud chatbot guesses dates", "Cited OCR + honest “could not verify”"),
        ("Needs internet", "Airplane-mode Snapdragon NPU"),
    ]
    # header
    rr(d, (70, 170, 900, 240), 12, fill=(80, 90, 105), outline=None)
    rr(d, (920, 170, 1850, 240), 12, fill=GOLD)
    d.text((100, 188), "THEM", font=F_BB(24), fill=WHITE)
    d.text((950, 188), "US", font=F_BB(24), fill=NAVY)
    y = 260
    for left, right in rows[1:]:
        rr(d, (70, y, 900, y + 100), 12, fill=NAVY2)
        rr(d, (920, y, 1850, y + 100), 12, fill=(32, 52, 42))
        d.text((100, y + 32), left, font=F_B(22), fill=MUTED)
        d.text((950, y + 32), "✓  " + right, font=F_BB(22), fill=(180, 230, 200))
        y += 112
    footer(d, 11)
    return im


def s12():
    im, _ = bleed(os.path.join(AI, "verid_judges_pick.png"))
    im = veil(im, 0, W, 150)
    d = ImageDraw.Draw(im)
    pill(d, (70, 50), 340, 40, "LIVE  ·  3 MINUTES", GOLD, NAVY)
    d.text((70, 110), "Show the path. Stop.", font=F_H1(48), fill=WHITE)
    steps = [
        ("0:00", "Dashboard + Health Center (red AC, amber washer)"),
        ("0:45", "Point at the washer → HUD + “How old is this?”"),
        ("1:30", "1-click Electrolux → OCR + YOLO → mint DPP"),
        ("2:15", "Claim pack + airplane-mode scan"),
    ]
    x = 70
    for t, b in steps:
        rr(d, (x, 210, x + 430, 420), 18, fill=(12, 22, 36, 220), outline=GOLD, width=2)
        d.text((x + 24, 230), t, font=F_H1(32), fill=GOLD2)
        by = 290
        for line in wrap(d, b, F_B(20), 380):
            d.text((x + 24, by), line, font=F_B(20), fill=WHITE)
            by += 28
        x += 460
    d.text((70, 470), "We built it. We measured it. It runs on the phone in your pocket.", font=F_H2(28), fill=GOLD2)
    three = [
        ("Built", "Vite + React · FastAPI · YOLOv8 · RapidOCR · live QR scanner"),
        ("Proved", "98.10% mAP@50 · SHA-256 DPP · Point-and-Ask HUD"),
        ("Scales", "Every home. Every warranty. Private by default."),
    ]
    x = 70
    for t, b in three:
        rr(d, (x, 540, x + 580, 760), 16, fill=(12, 22, 36, 220), outline=GOLD, width=1)
        d.text((x + 24, 560), t, font=F_BB(24), fill=GOLD)
        for j, line in enumerate(wrap(d, b, F_B(20), 520)):
            d.text((x + 24, 616 + j * 30), line, font=F_B(20), fill=WHITE)
        x += 610
    d.text((70, 800), "Team Verid   ·   github.com/ATS-AI-6278/IQ-Hackathon   ·   Ready for judging", font=F_BB(24), fill=WHITE)
    d.text((70, 860), "Ask the house. Point at the machine. File the claim. Stay offline.", font=F_H2(24), fill=GOLD2)
    footer(d, 12)
    return im


def to_rgb(im):
    if im.mode == "RGBA":
        bg = Image.new("RGB", im.size, NAVY)
        bg.paste(im, mask=im.split()[3])
        return bg
    return im.convert("RGB")


def build():
    os.makedirs(OUT_PNG, exist_ok=True)
    os.makedirs(DESKTOP, exist_ok=True)
    makers = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12]
    pngs = []
    rgb_pages = []
    for i, fn in enumerate(makers, 1):
        print(f"Rendering slide {i:02d}...")
        im = to_rgb(fn())
        path = os.path.join(OUT_PNG, f"slide_{i:02d}.png")
        im.save(path, "PNG", optimize=True)
        pngs.append(path)
        rgb_pages.append(im)

    pdf_path = os.path.join(DESKTOP, "Verid_Championship_Pitch.pdf")
    rgb_pages[0].save(pdf_path, save_all=True, append_images=rgb_pages[1:], resolution=150, quality=95)
    print("PDF:", pdf_path)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    for path in pngs:
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(path, 0, 0, width=Inches(13.333), height=Inches(7.5))
    pptx_path = os.path.join(DESKTOP, "Verid_Championship_Pitch.pptx")
    prs.save(pptx_path)
    print("PPTX:", pptx_path)

    # also copy PNG set for judges who want images
    img_dir = os.path.join(DESKTOP, "Championship_Slide_PNGs")
    os.makedirs(img_dir, exist_ok=True)
    for p in pngs:
        shutil.copy2(p, os.path.join(img_dir, os.path.basename(p)))
    print("PNGs:", img_dir)
    return pptx_path, pdf_path


if __name__ == "__main__":
    build()
