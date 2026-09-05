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
│       │   ├── detector.py      # YOLO appliance detector + Qwen2.5-VL fallback
│       │   ├── extractor.py     # Document understanding & anti-hallucination selection
│       │   ├── ocr.py           # RapidOCR (ONNX) + Tesseract text engine
│       │   └── runner.py        # CLI execution bridge
│       ├── models/
│       │   └── yolo26n.pt       # YOLO appliance detection weights
│       ├── requirements.txt     # Python dependencies
│       └── test_ai.py           # AI test suite
│
├── packages/
│   ├── api-spec/                # OpenAPI 3.1 schema specification
│   ├── api-zod/                 # Generated Zod validation schemas & TypeScript types
│   └── api-client-react/        # React Query hooks for frontend
│
└── samples/                     # Test invoices, warranty cards, and appliance photos
```

---

## Core Capabilities & AI Workflows

1. **Document Analysis (`/api/passport/analyze-document`)**:
   - Accepts uploaded invoices, receipts, and warranty cards (JPG, PNG, PDF).
   - Preprocesses images with contrast enhancement, unsharp masking, and LANCZOS upscaling.
   - Extracts text via RapidOCR (ONNX) or Tesseract.
   - Applies deep document understanding via Qwen2.5-VL / Ollama with strict anti-hallucination and checkbox selection rules.
   - Gracefully falls back to high-fidelity regex/heuristic extraction if Ollama is offline.
   - Normalizes purchase dates, prices, currencies, and separates multi-product documents.

2. **Physical Product Identification (`/api/product/identify`)**:
   - Processes photos taken with device camera or uploaded.
   - Runs YOLO (`models/yolo26n.pt`) detection to identify household appliances (refrigerator, TV, microwave, oven, laptop, etc.).
   - Employs Qwen2.5-VL vision semantic fallback if YOLO detects no candidate.
   - Generates normalized bounding box coordinates and extracts visual features.

3. **Product Matching & Linking (`/api/product/match` & `/api/passport/:id/link-product`)**:
   - Compares detected physical attributes (brand, model, category, serial number) against existing passports in the registry.
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

```bash
# Start Node API Server (Port 5000)
pnpm dev:api

# Start Web UI (Port 5173, with proxy to :5000)
pnpm dev:web

# Start Python AI Service (Port 8000, optional — CLI bridge runs automatically if not started)
pnpm dev:ai
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
