# Verid - Digital Product Passport Platform

A unified, production-ready enterprise platform for creating, verifying, and matching digital product passports from physical documents and products using AI computer vision and optical character recognition.

---

## Architecture Overview

```
c:\Users\acer\Pictures\IQ\
├── apps/
│   ├── web/                     # React 19 + Tailwind CSS frontend application
│   │   ├── src/
│   │   │   ├── components/      # UI components & Error Boundary
│   │   │   ├── pages/           # Dashboard, Passports, Create, Scan, Activity, Settings
│   │   │   └── App.tsx          # Navigation, state, and router
│   │   └── vite.config.ts       # Vite configuration with API proxy
│   │
│   ├── api/                     # Node.js Express 5 API server
│   │   ├── src/
│   │   │   ├── routes/          # Passports, Products, Activity, System status
│   │   │   ├── services/        # AI document analysis & product identification
│   │   │   ├── lib/             # Passport store & Python AI client bridge
│   │   │   └── app.ts           # Express configuration & 50MB payload limits
│   │   └── build.mjs            # Production esbuild bundler
│   │
│   └── ai-service/              # Python AI / ML microservice & CLI bridge
│       ├── app/
│       │   ├── main.py          # FastAPI application (/analyze-document, /identify-product, /status)
│       │   ├── detector.py      # Dual-engine YOLO (custom + COCO) + Qwen-VL fallback
│       │   ├── extractor.py     # Document understanding & anti-hallucination selection
│       │   ├── ocr.py           # RapidOCR (ONNX) + Tesseract text engine
│       │   └── runner.py        # CLI execution bridge
│       ├── models/
│       │   ├── custom_appliances.pt # Fine-tuned YOLO (98.1% mAP@50 on AC, Washer, Closet, Purifier, Cot)
│       │   └── yolo26n.pt       # COCO Foundation YOLO weights
│       ├── requirements.txt     # Python dependencies
│       └── test_ai.py           # AI test suite
│
├── Model/                       # Custom YOLO Training & Dataset Pipeline
│   ├── dataset/                 # 292 unified & clamped 5-class annotated dataset
│   ├── prepare_dataset.py       # Dataset stratification and verification
│   ├── train_yolo.py            # Automated training script (25 epochs, 98.1% mAP)
│   └── evaluate_model.py        # Validation split & live sample evaluator
│
├── packages/
│   ├── api-spec/                # OpenAPI 3.1 schema specification
│   ├── api-zod/                 # Generated Zod validation schemas & TypeScript types
│   └── api-client-react/        # React Query hooks for frontend
│
└── samples/                     # Test invoices, warranty cards, and appliance photos
```

> 📖 **Complete Technical Documentation**: See [PROJECT_DOCUMENTATION.md](file:///c:/Users/acer/Pictures/IQ/PROJECT_DOCUMENTATION.md) for full architecture specs, model evaluation metrics, and hackathon evaluation guides.

---

## Core Capabilities & AI Workflows

1. **Document Analysis (`/api/passport/analyze-document`)**:
   - Accepts uploaded invoices, receipts, and warranty cards (JPG, PNG, PDF).
   - Preprocesses images with contrast enhancement, unsharp masking, and LANCZOS upscaling.
   - Extracts text via RapidOCR (ONNX) or Tesseract.
   - Applies deep document understanding via Qwen2.5-VL / Ollama with strict anti-hallucination rules.
   - Gracefully falls back to high-fidelity regex/heuristic extraction if Ollama is offline.
   - Normalizes purchase dates, prices, currencies, and separates multi-product documents.

2. **Physical Product Identification (`/api/product/identify`)**:
   - Processes photos taken with mobile camera or uploaded.
   - Runs **fine-tuned custom YOLO** (`models/custom_appliances.pt`) for specialized household items (**Air Conditioner, Washing Machine, Closet / Wardrobe, Water Purifier, Cot / Bed**) at **98.1% mAP@50** and **<100ms CPU latency**.
   - Falls back to general COCO YOLO (`models/yolo26n.pt`) for electronics (Laptop, TV, Refrigerator, Microwave, Smartphone).
   - Employs bounded Qwen2.5-VL vision semantic fallback if neither YOLO detects a candidate.
   - Generates normalized bounding box coordinates and authentic visual features without hallucination.

3. **Product Matching & Linking (`/api/product/match` & `/api/passport/:id/link-product`)**:
   - Compares detected physical attributes against existing passports with semantic product alias mapping (`washer` <-> `washing machine`, `ac` <-> `air conditioner`, `almirah` <-> `closet`).
   - Computes weighted match confidence scores and links physical scans to source evidence.

4. **Service Health Monitoring (`/api/system/status`)**:
   - Live health checks for Passport API, OCR Engine, Vision Model (Ollama), and Product Detection (YOLO).

---

## Quick Start

### Prerequisites
- Node.js v18+ (Node v24 recommended)
- pnpm v9+ (v11 recommended)
- Python 3.10+ with packages in `apps/ai-service/requirements.txt`

### 1. Install Dependencies
```bash
# Node dependencies
pnpm install

# Python dependencies (if not already installed)
pip install -r apps/ai-service/requirements.txt
```

### 2. Run All Services in Development Mode

#### 🚀 Option A: Run All 3 Simultaneously in ONE Command (Recommended)
```bash
pnpm dev:all
# or
pnpm start:all
```
*(Or simply double-click `run.bat` or run `.\run.ps1` in PowerShell)*

#### Option B: Run in Separate Terminals
```bash
# Terminal 1: Python AI Service (Port 8000)
pnpm dev:ai

# Terminal 2: Node API Server (Port 5000)
pnpm dev:api

# Terminal 3: Web UI (Port 5173, with proxy to :5000)
pnpm dev:web
```

### 3. Build for Production

```bash
pnpm build
```

### 4. Run Automated Tests

```bash
# Test Python AI pipeline (YOLO + OCR + Extractor)
pnpm test:ai

# Test End-to-End API Integration
python test_e2e.py

# Monorepo TypeScript check
pnpm typecheck
```

---

## Technologies Used

- **Frontend**: React 19, Tailwind CSS v4, Lucide Icons, TanStack Query v5, Wouter, Framer Motion
- **Backend**: Node.js, Express 5, Pino Logger, CORS
- **AI / ML**: Ultralytics YOLO (`yolo26n.pt`), RapidOCR (ONNX), PyTorch, TorchVision, OpenCV, PIL, Ollama (Qwen2.5-VL), FastAPI, Uvicorn
- **API Specification & Validation**: OpenAPI 3.1, Zod, Orval
