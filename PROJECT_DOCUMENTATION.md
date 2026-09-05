# Verid - Digital Product Passport (DPP) Platform
### iQOO Hackathon 2026 · Technical Documentation & Deployment Guide

---

## 1. Executive Summary & Vision

**Verid** is an AI-powered **Digital Product Passport (DPP)** system that transforms ephemeral paper receipts, warranty cards, and invoices into living, verifiable asset passports. 

### The Problem It Solves:
1. **Lost Warranties & Receipts**: Households lose thousands annually because paper warranty cards fade, invoices get misplaced, and warranty expiration dates pass unnoticed.
2. **Fraudulent Resale & Insurance Claims**: Buying secondhand appliances often involves unverified ownership claims and faked receipts.
3. **Circular Economy & Repairability**: Global standards (such as the EU Ecodesign and DPP directives) require products to maintain transparent maintenance histories, repairability scores, and component provenance.

### The Solution:
Verid creates a **cryptographically bound link** between two pieces of evidence:
* **The Commercial Document** (processed via RapidOCR + zero-hallucination semantic parsing)
* **The Physical Product** (verified via a custom fine-tuned YOLO computer vision model running sub-100ms on edge CPU)

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                │
│        React 19 + Vite + Tailwind CSS + TanStack React Query            │
│                 (Web Dashboard, Mobile Scanner, Detail View)            │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP (port 5173 -> 5000)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY / BACKEND                         │
│                    Node.js Express 5 + TypeScript                       │
│  - Passport CRUD & In-Memory / SQLite Store                             │
│  - Semantic Alias Matching Service (Washer <-> Washing Machine, etc.)   │
│  - Dual HTTP / Subprocess Bridge to AI Engine                           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP (port 5000 -> 8000)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           AI ENGINE (FASTAPI)                           │
│                   Python 3.10 + PyTorch + OpenCV                        │
│                                                                         │
│  ┌───────────────────────────┐         ┌─────────────────────────────┐  │
│  │   DOCUMENT UNDERSTANDING  │         │   PHYSICAL OBJECT DETECTOR  │  │
│  │  - Image Preprocessing    │         │  - Custom YOLO (98.1% mAP)  │  │
│  │  - RapidOCR (ONNX)        │         │    [AC, Washer, Closet,     │  │
│  │  - Tesseract Fallback     │         │     Water Purifier, Cot]    │  │
│  │  - Bounded Qwen-VL (4s)   │         │  - COCO YOLO (Laptop, TV,   │  │
│  │  - Zero-Fabrication Parser│         │    Fridge, Microwave, Phone)│  │
│  └───────────────────────────┘         └─────────────────────────────┘  │
│                                                                         │
│  Lifespan Pre-warming: PyTorch & OCR warm at boot (sub-200ms latency)  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Machine Learning Model & Training Pipeline

### Custom Appliance YOLO Architecture
* **Backbone**: Nano YOLO (`yolov8n.pt`, 73 layers, 3,006,623 parameters, 8.1 GFLOPs)
* **Training Dataset**: 292 validated, uncorrupted images with normalized & clamped floating-point coordinates.
* **Stratified Split**: 236 training images (80%), 56 validation images (20%).
* **Target Classes**:
  1. `0: AC` (Air Conditioner)
  2. `1: washing machine`
  3. `2: closet` (Wardrobe / Almirah)
  4. `3: water purifier`
  5. `4: cot` (Bed / Bedstead)
* **Training Hyperparameters**:
  - Image size: `640x640`
  - Epochs: `25`
  - Batch size: `16`
  - Optimizer: Automatic AdamW with cosine learning rate schedule
  - Device: CPU (`Intel Core i3-N305`)
  - Patience: 10 epochs early stopping

### Final Evaluation Metrics (Validation Split):
* **Overall Precision (P)**: **99.29%**
* **Overall Recall (R)**: **98.57%**
* **Overall mAP@50**: **98.10%**
* **Overall mAP@50-95**: **84.45%**
* **Per-Image Inference Latency**: **69.4 ms – 96.5 ms** on CPU

```
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95)
                   all         56         57      0.993      0.986      0.981      0.844
                    AC          4          4      0.988      1.000      0.995      0.658
       washing machine         16         16      0.991      1.000      0.995      0.958
                closet         10         10      0.997      1.000      0.995      0.926
        water purifier         13         14      0.997      0.929      0.925      0.825
                   cot         13         13      0.991      1.000      0.995      0.855
```

---

## 4. How to Run the Project (Step-by-Step)

### Prerequisites:
1. **Node.js**: v20+ and **pnpm** installed (`corepack enable && corepack prepare pnpm@latest --activate`)
2. **Python**: 3.10 or 3.11 with `pip`
3. **Git**: Installed and configured

---

### Step 1: Install Dependencies

#### Backend & Frontend (Root Directory):
```bash
cd c:\Users\acer\Pictures\IQ
pnpm install
```

#### AI Python Microservice:
```bash
cd c:\Users\acer\Pictures\IQ\apps\ai-service
pip install -r requirements.txt
```

---

### Step 2: Start the Services

The application consists of three services running concurrently. You can start each in its own terminal window or shell.

#### Terminal 1: Start the Python AI Microservice (Port 8000)
```bash
cd c:\Users\acer\Pictures\IQ\apps\ai-service
python -m uvicorn app.main:app --port 8000
```
> **What this does**: Boots FastAPI, pre-warms the custom appliance YOLO detector and RapidOCR engine, and serves `/analyze-document`, `/identify-product`, and `/status`.

#### Terminal 2: Start the Express API Backend (Port 5000)
```bash
cd c:\Users\acer\Pictures\IQ
pnpm --filter @workspace/api-server dev
```
> **What this does**: Boots the Express 5 server with TypeScript compilation on `http://localhost:5000/api`, handling passport management, matching logic, and AI routing.

#### Terminal 3: Start the Vite Web Frontend (Port 5173)
```bash
cd c:\Users\acer\Pictures\IQ
pnpm --filter @workspace/digital-product-passport dev
```
> **What this does**: Serves the React 19 application at `http://localhost:5173` with automatic API proxying to port 5000.

---

### Step 3: Verify the System Status

You can verify that all three microservices are healthy and connected by running:

```bash
python -c "
import urllib.request, json
print('FastAPI AI (8000):', urllib.request.urlopen('http://127.0.0.1:8000/health').status)
print('Express API (5000):', urllib.request.urlopen('http://127.0.0.1:5000/api/healthz').status)
print('Vite Web (5173):   ', urllib.request.urlopen('http://127.0.0.1:5173').status)
"
```

You can also visit the **Settings / Trust Center** page in your browser at:
`http://localhost:5173/settings`

It will display live status for:
* **Backend**: Passport AI Engine (`connected`)
* **OCR Engine**: RapidOCR (ONNX) (`connected`)
* **Vision Model**: Ollama / Qwen-VL (`connected` or `heuristic fallback`)
* **Product Detection**: `Active: Fine-tuned Custom Appliances + COCO Foundation` (`connected`)

---

## 5. Automated Testing & Model Verification

### Run the Full-Stack API Test Suite:
```bash
python tests/test_api_suite.py
```
* Runs 11 end-to-end integration tests:
  1. Health check
  2. System service statuses
  3. Passport listing
  4. Dashboard analytics
  5. Activity timeline
  6. Single passport retrieval
  7. Passport creation
  8. Passport field patching
  9. Visual product detection via YOLO
  10. Product matching and linking
  11. Document OCR & analysis

### Run the Custom YOLO Model Evaluation:
```bash
python Model/evaluate_model.py
```
* Computes class-by-class Precision, Recall, and mAP@50 against the validation dataset and executes live sample inference on real test images.

### Run Comprehensive Model Audit:
```bash
python apps/ai-service/audit_models.py
```
* Audits YOLO detection and RapidOCR text extraction across all sample documents and images in `samples/`.

---

## 6. End-to-End User Flow (How to Demo)

1. **Dashboard (`/`)**:
   - Displays real-time metrics: Total Passports, Physically Verified Passports, Documents Processed, and Verification Rate.
   - Shows recent activity feed with timestamped verification events.

2. **Create a Passport (`/create`)**:
   - **Step 1 (Upload)**:
     - Drag & drop or browse a purchase receipt/warranty document (`samples/image2.png`).
     - Optionally add a physical photo of the product (`samples/img.jpg`).
     - Click **Analyze Document & Verify Physical Product**.
   - **Step 2 (Analyze)**:
     - The AI pipeline extracts commercial fields via OCR and detects the appliance via YOLO in $<2$ seconds.
   - **Step 3 (Review)**:
     - Review the extracted product name, brand, model, serial number, purchase date, price, and warranty.
     - Notice the physical verification badge indicating YOLO detected the device.
   - **Step 4 (Save)**:
     - The passport is minted with a unique identifier (`DPP-00028`) and stored in the library.

3. **Product Scanner (`/scan`)**:
   - Upload any photo of a home appliance or use a mobile camera.
   - Instant YOLO bounding box classification identifies the product.
   - The matching engine searches existing passports and computes a match score based on serial number, model, brand, category, and visual form factor.
   - Click **Link Product** to certify the physical device.

---

## 7. Recommended Next Steps for Hackathon Optimization

1. **1-Click Judge Demo Presets**: Add instant sample buttons on the upload form so judges can see the end-to-end pipeline run with 1 click without needing their own files.
2. **"Scan with Phone" QR Connect**: Display a QR code on the `/scan` desktop page so judges can scan it with their phone camera to open the camera scanner directly on mobile.
3. **PDF Passport Export**: Add an "Export Official Passport" button that generates a downloadable, verifiable certificate with an EU Repairability Index and warranty countdown.
4. **Interactive Bounding Box Overlay**: Render an interactive bounding box on detected product photos showing coordinates and detection confidence.
