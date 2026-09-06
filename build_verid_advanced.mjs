import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
const artifactToolPath = "C:\\Users\\acer\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules\\@oai\\artifact-tool\\dist\\artifact_tool.mjs";
const { Presentation, PresentationFile } = await import(pathToFileURL(artifactToolPath).href);

const workspaceDir = "C:\\Users\\acer\\Pictures\\IQ";
const SKILL_DIR = "C:\\Users\\acer\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.904.11930\\skills\\presentations";
const RUNTIME_PYTHON = "C:\\Users\\acer\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";
const TMP_DIR = path.join(workspaceDir, ".codex-verid-build");
const OUT_DIR = path.join(workspaceDir, "output", "pptx");
const FINAL_PPTX = path.join(OUT_DIR, "Verid_Household_Intelligence_OS_Advanced.pptx");
const assetDir = path.join(workspaceDir, "presentation_assets");
const { resolvePresentationFont, finalizePresentation } = await import(pathToFileURL(path.join(SKILL_DIR, "container_tools", "artifact_tool_utils.mjs")).href);

await fs.mkdir(TMP_DIR, { recursive: true });
await fs.mkdir(OUT_DIR, { recursive: true });
const font = resolvePresentationFont();
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

const C = {
  ink: "#07111F", navy: "#0E1C2F", panel: "#12283E", paper: "#F5F0E7",
  white: "#FFFFFF", lime: "#CBFF4D", gold: "#FFC857", sky: "#71D9FF",
  mint: "#69E0B2", coral: "#FF8364", fog: "#B9C8D8", line: "#29445D",
};
const note = "Source: PROJECT_DOCUMENTATION.md, Team Verid, iQOO Hackathon 2026. Project screenshots are supplied by the team.";

function rect(slide, x, y, w, h, fill, radius = 0, line = "none") {
  return slide.shapes.add({ geometry: radius ? "roundRect" : "rect", position: { left: x, top: y, width: w, height: h }, fill, line: line === "none" ? { fill: "none", width: 0 } : { fill: line, width: 1 }, borderRadius: radius || undefined });
}
function text(slide, value, x, y, w, h, { size = 18, color = C.white, bold = false, align = "left", italic = false } = {}) {
  const s = slide.shapes.add({ geometry: "textbox", position: { left: x, top: y, width: w, height: h }, fill: "none", line: { fill: "none", width: 0 } });
  s.text = value;
  s.text.style = { typeface: font, fontSize: size, color, bold, italic, autoFit: "shrinkText", paragraphAlignment: align };
  return s;
}
async function image(slide, filename, x, y, w, h, alt, fit = "cover") {
  const bytes = await fs.readFile(path.join(assetDir, filename));
  const contentType = filename.toLowerCase().endsWith(".jpg") ? "image/jpeg" : "image/png";
  return slide.images.add({ blob: bytes, contentType, alt, fit, geometry: "roundRect", borderRadius: "rounded-2xl", position: { left: x, top: y, width: w, height: h } });
}
function page(slide, n, dark = true) {
  slide.background.fill = dark ? C.ink : C.paper;
  text(slide, "VERID / HOUSEHOLD INTELLIGENCE OS", 54, 676, 490, 18, { size: 10, color: dark ? C.fog : C.navy, bold: true });
  text(slide, String(n).padStart(2, "0"), 1170, 676, 56, 18, { size: 11, color: dark ? C.lime : C.navy, bold: true, align: "right" });
}
function kicker(slide, value, x = 58, y = 46, color = C.lime) { text(slide, value.toUpperCase(), x, y, 450, 22, { size: 12, color, bold: true }); }
function title(slide, value, x = 58, y = 82, w = 720, color = C.white) { text(slide, value, x, y, w, 115, { size: 40, color, bold: true }); }
function rule(slide, x, y, w, color = C.line) { rect(slide, x, y, w, 2, color); }
function metric(slide, value, label, x, y, w, accent = C.lime) {
  text(slide, value, x, y, w, 48, { size: 31, color: accent, bold: true });
  text(slide, label, x, y + 48, w, 38, { size: 14, color: C.fog });
}
function step(slide, n, heading, body, x, y, w, accent) {
  text(slide, n, x, y, 42, 34, { size: 15, color: accent, bold: true });
  text(slide, heading, x, y + 38, w, 32, { size: 19, color: C.white, bold: true });
  text(slide, body, x, y + 76, w, 68, { size: 14, color: C.fog });
}

// 1. Cover
{
  const s = deck.slides.add(); page(s, 1, true);
  rect(s, 0, 0, 1280, 720, C.ink);
  await image(s, "15_household_product_graph.jpg", 766, 0, 514, 720, "AI illustration of a connected household product graph");
  rect(s, 690, 0, 220, 720, C.ink);
  kicker(s, "iQOO Hackathon 2026 / AI Track");
  title(s, "Your home has memory.\nIt just needs a system.", 58, 106, 655);
  text(s, "Verid connects products, invoices, manuals, and maintenance into a private household intelligence layer.", 58, 304, 570, 80, { size: 20, color: C.fog });
  rule(s, 58, 430, 514, C.lime);
  text(s, "Verified ownership\nActionable care\nPrivate AI", 58, 456, 450, 100, { size: 22, color: C.white, bold: true });
  text(s, "A working product for the moment homeowners need it most: when something breaks, expires, or gets forgotten.", 58, 585, 555, 52, { size: 15, color: C.fog });
  s.speakerNotes.textFrame.setText(note);
}

// 2. Problem
{
  const s = deck.slides.add(); page(s, 2, false);
  kicker(s, "The household ownership gap", 58, 45, C.navy);
  title(s, "A product’s history disappears the moment it enters the home", 58, 80, 860, C.navy);
  text(s, "Documents, hardware evidence, and service events live apart. That makes a simple warranty claim or maintenance decision unnecessarily hard.", 58, 186, 865, 50, { size: 18, color: "#496277" });
  const items = [
    ["01", "Proof is scattered", "Invoices sit in chat threads, folders, and drawers while model and serial details fade from view."],
    ["02", "Care arrives too late", "Warranty deadlines, filters, cleaning, and service history surface only after a failure."],
    ["03", "Files cannot answer", "A storage folder cannot connect a real appliance to evidence, a manual, and the next action."],
  ];
  let x = 58;
  for (const [n, h, b] of items) { rect(s, x, 316, 348, 215, C.white, 18, "#D8D0C3"); text(s, n, x + 24, 340, 45, 28, { size: 14, color: C.coral, bold: true }); text(s, h, x + 24, 382, 285, 36, { size: 21, color: C.navy, bold: true }); text(s, b, x + 24, 432, 282, 65, { size: 14, color: "#526C81" }); x += 382; }
  text(s, "The missed opportunity: turn ownership records into a reliable, usable household memory.", 58, 584, 1000, 42, { size: 22, color: C.navy, bold: true });
  s.speakerNotes.textFrame.setText(note);
}

// 3. Verified passport
{
  const s = deck.slides.add(); page(s, 3, true);
  kicker(s, "The core product", 58, 45);
  title(s, "One verified passport for every important product", 58, 80, 800);
  text(s, "Verid pairs commercial evidence with a real product photo before it creates a household record.", 58, 185, 760, 40, { size: 18, color: C.fog });
  await image(s, "01_input_warranty_document.png", 58, 275, 245, 250, "Warranty document source");
  await image(s, "02_input_physical_product_photo.png", 332, 275, 245, 250, "Physical appliance photo source");
  text(s, "DOCUMENT\nEVIDENCE", 58, 538, 245, 44, { size: 12, color: C.sky, bold: true, align: "center" });
  text(s, "HARDWARE\nEVIDENCE", 332, 538, 245, 44, { size: 12, color: C.mint, bold: true, align: "center" });
  text(s, "+", 608, 355, 44, 56, { size: 34, color: C.lime, bold: true, align: "center" });
  rect(s, 665, 287, 206, 207, C.panel, 18, C.line);
  text(s, "RapidOCR\n+ YOLO", 689, 323, 158, 65, { size: 25, color: C.lime, bold: true, align: "center" });
  text(s, "Extracts facts\nChecks the physical object", 686, 413, 164, 46, { size: 13, color: C.fog, align: "center" });
  await image(s, "07_passport_minted_verified.png", 920, 218, 295, 345, "Verified product passport");
  text(s, "A durable record with evidence, identity, warranty, manual, service history, and next actions.", 670, 548, 520, 44, { size: 15, color: C.fog, align: "center" });
  s.speakerNotes.textFrame.setText(note);
}

// 4. Model proof
{
  const s = deck.slides.add(); page(s, 4, false);
  kicker(s, "Computer vision proof", 58, 45, C.navy);
  title(s, "The vision model recognizes the physical side of ownership", 58, 80, 815, C.navy);
  text(s, "A custom YOLOv8n detector identifies five household classes from real images, then connects the result to the relevant passport.", 58, 183, 800, 42, { size: 18, color: "#496277" });
  metric(s, "99.29%", "Precision on the validation split", 58, 265, 235, C.navy);
  metric(s, "98.10%", "mAP@50 across five target classes", 325, 265, 265, C.coral);
  metric(s, "69-97 ms", "Per-image CPU inference latency", 622, 265, 265, C.navy);
  await image(s, "08_model_confusion_matrix.png", 58, 385, 420, 235, "Confusion matrix from the custom appliance detector", "contain");
  await image(s, "09_model_training_metrics_curves.png", 515, 385, 420, 235, "Training metric curves from the custom appliance detector", "contain");
  rect(s, 968, 385, 250, 235, C.navy, 18);
  text(s, "Target classes", 994, 414, 200, 28, { size: 19, color: C.lime, bold: true });
  text(s, "AC\nWashing machine\nCloset\nWater purifier\nCot", 994, 460, 190, 122, { size: 17, color: C.white, bold: true });
  s.speakerNotes.textFrame.setText(note);
}

// 5. Daily experience
{
  const s = deck.slides.add(); page(s, 5, true);
  kicker(s, "The daily experience", 58, 45);
  title(s, "Point. Ask. Act.", 58, 82, 460);
  text(s, "A household record is only useful when it answers a question in the moment.", 58, 178, 500, 46, { size: 18, color: C.fog });
  await image(s, "13_point_and_ask_camera_ar.jpg", 58, 270, 355, 275, "Point-and-Ask augmented-reality appliance view");
  await image(s, "14_household_health_attention_center.jpg", 447, 270, 355, 275, "Household health and attention center");
  await image(s, "03_dashboard_overview.png", 836, 270, 356, 275, "Household dashboard overview");
  text(s, "See the appliance", 58, 567, 355, 26, { size: 17, color: C.lime, bold: true, align: "center" });
  text(s, "Find what needs attention", 447, 567, 355, 26, { size: 17, color: C.lime, bold: true, align: "center" });
  text(s, "Ask the whole house", 836, 567, 356, 26, { size: 17, color: C.lime, bold: true, align: "center" });
  text(s, "“When does my washing machine warranty expire?”", 58, 626, 550, 28, { size: 16, color: C.white, italic: true });
  s.speakerNotes.textFrame.setText(note);
}

// 6. Trust and privacy
{
  const s = deck.slides.add(); page(s, 6, false);
  kicker(s, "Trust is a product feature", 58, 45, C.navy);
  title(s, "Every answer carries its evidence", 58, 80, 650, C.navy);
  text(s, "Verid shows the answer, why it reached it, and the source record. When the system cannot verify a detail, it says so.", 58, 182, 735, 50, { size: 18, color: "#496277" });
  await image(s, "04_trust_center_ai_models.png", 58, 270, 510, 290, "Trust center product screen");
  await image(s, "12_official_dpp_certificate_seal.png", 840, 235, 333, 355, "Digital product passport certificate and seal", "contain");
  const proof = [["Evidence", "Invoice, product photo, manual, service log"], ["Reasoning", "A plain-language explanation for each result"], ["Provenance", "Traceable source record and confidence check"]];
  let y = 286;
  for (const [h, b] of proof) { text(s, h, 620, y, 165, 25, { size: 18, color: C.navy, bold: true }); text(s, b, 620, y + 32, 188, 42, { size: 14, color: "#526C81" }); y += 95; }
  text(s, "Offline mode keeps household data local while the system processes documents and answers questions.", 58, 615, 930, 34, { size: 17, color: C.navy, bold: true });
  s.speakerNotes.textFrame.setText(note);
}

// 7. Demo sequence
{
  const s = deck.slides.add(); page(s, 7, true);
  kicker(s, "Live demo", 58, 45);
  title(s, "Three minutes to show the complete loop", 58, 80, 740);
  text(s, "The demo makes the product tangible: capture evidence, recognize the appliance, prove the passport, then trigger an action.", 58, 184, 830, 40, { size: 18, color: C.fog });
  step(s, "01", "Connect a phone", "Scan the local QR bridge and open the live camera, with no app installation.", 58, 300, 240, C.lime);
  step(s, "02", "Point at a product", "The detector recognizes the appliance and retrieves its linked household passport.", 344, 300, 240, C.sky);
  step(s, "03", "Inspect the proof", "Show the evidence-backed record, warranty status, and source documents.", 630, 300, 240, C.gold);
  step(s, "04", "Take the next action", "Surface a maintenance alert or prepare a complete warranty claim pack.", 916, 300, 245, C.mint);
  await image(s, "11_phone_connect_qr_bridge.png", 58, 487, 305, 140, "Phone QR bridge screen");
  await image(s, "10_live_scanner_match_result.png", 405, 487, 305, 140, "Live appliance scanner match result");
  await image(s, "06_review_ocr_and_yolo_detection.png", 752, 487, 405, 140, "OCR and YOLO review screen");
  s.speakerNotes.textFrame.setText(note);
}

// 8. Close
{
  const s = deck.slides.add(); page(s, 8, true);
  rect(s, 0, 0, 1280, 720, C.ink);
  await image(s, "05_create_dual_upload_populated.png", 793, 85, 415, 503, "Verid product intake screen");
  kicker(s, "Why Verid", 58, 58);
  title(s, "A real household system,\nnot another document folder.", 58, 97, 635);
  text(s, "Verid combines working vision, document intelligence, grounded assistance, and on-device privacy into one connected experience.", 58, 298, 590, 68, { size: 19, color: C.fog });
  rule(s, 58, 416, 526, C.lime);
  metric(s, "Working demo", "Phone-first scanner, product passport, attention center", 58, 452, 238, C.lime);
  metric(s, "Verified ML", "98.10% mAP@50 on the supplied validation split", 328, 452, 260, C.gold);
  text(s, "Team Verid / Ready to show the household intelligence loop live", 58, 616, 630, 28, { size: 16, color: C.white, bold: true });
  s.speakerNotes.textFrame.setText(note);
}

const candidatePath = path.join(TMP_DIR, "verid-advanced-candidate.pptx");
await (await PresentationFile.exportPptx(deck)).save(candidatePath);
const requirements = { explicitTotalSlideCount: 8, requiredNativeTableOwnerSlides: [], requiredNativeChartOwnerSlides: [] };
await finalizePresentation({
  ...requirements,
  workspaceDir,
  candidatePath,
  finalPath: FINAL_PPTX,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-bullet-geometry", "--validate-heading-fit"],
  fontPolicy: { basis: "design", families: [font] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(TMP_DIR, "verid-advanced-validation.json"),
});
console.log(FINAL_PPTX);
