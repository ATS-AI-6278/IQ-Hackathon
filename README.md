<div align="center">

<img src="docs/images/hovira-hero.png" alt="Hovira - Household Intelligence OS" width="100%" />

# **Hovira**

### Your phone remembers everything you own.

An AI-powered **Household Intelligence OS** that turns scattered receipts and forgotten appliance manuals into a living, searchable household memory graph.

[![Live Demo](https://img.shields.io/badge/Live_Demo-hovira.netlify.app-22c55e?style=for-the-badge&logo=vercel&logoColor=white)](https://hovira.netlify.app/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=for-the-badge)](LICENSE)

</div>

---

## The Problem

Household ownership is broken. Purchase receipts rot in drawers. Warranty cards expire unclaimed. Appliance manuals vanish the moment you need them. Every family manages dozens of products with zero digital structure -- losing money on missed warranties and wasting hours hunting for information that should be instant.

---

## The Solution

Hovira transforms your phone into a household intelligence hub. Upload a photo of any receipt, invoice, or warranty card and Hovira's AI extracts every detail -- date, price, serial number, warranty window. Point your camera at any appliance and a fine-tuned computer vision model identifies it in under 100ms. Everything links into a unified **Household Product Graph** you can search, query, and act on.

---

## Why Hovira is Different

| Traditional Approach | Hovira |
|---|---|
| Store files in folders and forget them | AI extracts and structures data automatically |
| Manual data entry | OCR + Vision AI does the work |
| Generic cloud storage | Household-specific product graph |
| No physical product link | Camera identifies appliances and links them to documents |
| Reactive (find out warranty expired too late) | Proactive alerts and maintenance scheduling |

---

## Core AI Architecture

<div align="center">
<img src="docs/images/architecture.png" alt="Hovira System Architecture" width="90%" />
</div>

Hovira runs a **three-service architecture** orchestrated as a monorepo:

- **Python AI Microservice** (FastAPI, port 8000) -- YOLO detection, OCR extraction, document understanding
- **Node.js API Gateway** (Express 5, port 5000) -- routing, validation, passport management
- **React Frontend** (Vite, port 5173) -- dashboard, scanner, passport viewer

---

## Key Features

- **Dual-Evidence Intake** -- Upload commercial documents AND physical product photos
- **Custom YOLO Detector** -- Fine-tuned on 5 household appliance classes at **98.1% mAP@50**
- **Zero-Fabrication Extraction** -- Anti-hallucination OCR with strict provenance tracking
- **Cryptographic DPP Certificates** -- SHA-256 sealed Digital Product Passports with EU Ecodesign compliance markers
- **Phone-First QR Bridge** -- Instant mobile camera access with zero app installation
- **1-Click Demo Presets** -- Pre-loaded scenarios for instant evaluation

---

## How It Works

<div align="center">
<img src="docs/images/how-it-works.png" alt="How Hovira Works" width="90%" />
</div>

**Scan → Identify → Create Passport → Attach Documents → Build Household Memory → Ask Hovira → Get grounded insight**

**4 steps from photo to verified product passport:**

1. **Upload** -- Snap a photo of a receipt/invoice and a photo of the physical appliance
2. **Extract** -- AI pulls purchase date, price, serial number, warranty terms via OCR + document understanding
3. **Detect** -- Custom YOLO identifies the appliance class, draws verified bounding boxes, computes confidence scores
4. **Mint** -- A cryptographic DPP certificate is generated linking commercial evidence to physical proof

---

## Why This Matters

Hovira begins as a **Digital Product Passport** platform -- the kind the EU is mandating for consumer electronics -- but its true trajectory is **Private AI Household Intelligence**. Every receipt scanned, every appliance photographed, every warranty tracked adds a node to a household graph that no cloud service has access to. Your data stays local. Your intelligence compounds. Over time, Hovira evolves from a document tool into a household operating system that knows what you own, when it needs attention, and what it's worth.

---

## Future Vision

> The following capabilities are **not yet implemented**. They represent the planned evolution of Hovira into a full Household Intelligence OS.

| Capability | Description |
|---|---|
| **Spatial Memory** | Map products and documents to physical rooms and locations within your home |
| **Point-and-Ask Camera** | Real-time AR HUD overlay showing warranty status and health when pointing at any appliance |
| **Context & Season-Aware Intelligence** | Proactive advice that adapts to weather, seasons, and usage patterns (e.g., pre-summer AC servicing) |
| **Attention Center** | Priority-ranked dashboard: critical alerts, upcoming maintenance, consumable replacements |
| **Maintenance Intelligence** | Lifecycle event engine tracking installation, service history, consumable wear, and expiration countdowns |
| **AI Manual Assistant** | RAG-powered Q&A over uploaded appliance manuals -- ask "How do I clean the drain filter?" and get exact steps |
| **Household Timeline** | Chronological view of every purchase, service visit, and warranty event across all products |
| **Local / Offline Intelligence** | Full on-device pipeline via edge NPU -- zero cloud dependency, zero data leakage |

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, Tailwind CSS v4, Vite 7, TanStack Query v5, Wouter, Framer Motion, Lucide Icons |
| **API Gateway** | Node.js, Express 5, Pino Logger, CORS |
| **AI / ML** | Ultralytics YOLO, RapidOCR (ONNX), PyTorch, OpenCV, FastAPI, Uvicorn |
| **Vision Fallback** | Ollama (Qwen2.5-VL) for deep document understanding |
| **API Spec** | OpenAPI 3.1, Zod validation, Orval code generation |
| **Monorepo** | pnpm workspaces, esbuild, concurrently |
| **Deployment** | Netlify (frontend), local development (API + AI services) |

---

## Current Implementation vs. Future Vision

| Capability | Status |
|---|---|
| Document OCR extraction (invoices, receipts, warranties) | **Implemented** |
| Custom YOLO appliance detection (5 classes, 98.1% mAP) | **Implemented** |
| Cryptographic DPP certificate generation | **Implemented** |
| Phone QR bridge for mobile camera access | **Implemented** |
| Anti-hallucination extraction with provenance | **Implemented** |
| 1-click judge demo presets | **Implemented** |
| Service health monitoring dashboard | **Implemented** |
| "Ask My House" natural language interface | Future |
| Point-and-Ask AR camera mode | Future |
| Spatial room mapping | Future |
| Season-aware proactive intelligence | Future |
| Attention/priority center | Future |
| Maintenance lifecycle engine | Future |
| AI manual RAG assistant | Future |
| Offline edge-NPU pipeline | Future |

---

## Getting Started

### Prerequisites

- **Node.js** v18+ (v24 recommended)
- **pnpm** v9+ (v11 recommended)
- **Python** 3.10+ with pip

### Install Dependencies

```bash
# Node dependencies (monorepo)
pnpm install

# Python AI service dependencies
pip install -r apps/ai-service/requirements.txt
```

### Run All Services

```bash
# Start AI service (port 8000), API gateway (port 5000), and web UI (port 5173) in parallel
pnpm dev:all
```

Or on Windows, double-click `run.bat`.

### Run Individually

```bash
pnpm dev:ai     # Python AI Microservice
pnpm dev:api    # Node.js API Gateway
pnpm dev:web    # React Frontend
```

### Build for Production

```bash
pnpm build
```

### Run Tests

```bash
pnpm test:ai        # Python AI pipeline (YOLO + OCR + Extractor)
pnpm test:suite     # REST API integration tests
pnpm typecheck      # TypeScript type checking
```

---

## Project Structure

```
hovira/
├── apps/
│   ├── web/                 # React 19 + Tailwind CSS frontend
│   ├── api/                 # Express 5 API gateway
│   └── ai-service/          # Python FastAPI AI microservice
│       ├── app/
│       │   ├── main.py      # FastAPI routes
│       │   ├── detector.py  # YOLO dual-engine detection
│       │   ├── extractor.py # Document understanding
│       │   └── ocr.py       # RapidOCR + Tesseract
│       └── models/          # Custom + COCO YOLO weights
├── packages/
│   ├── api-spec/            # OpenAPI 3.1 schema
│   ├── api-zod/             # Zod validation schemas
│   └── api-client-react/    # React Query hooks
├── Model/                   # YOLO training pipeline & dataset
├── samples/                 # Test invoices, receipts, appliance photos
└── docs/
    ├── images/              # Hero, architecture, how-it-works visuals
    └── diagrams/            # System stack & flow diagrams
```

---

## Links

- **Live Demo:** [hovira.netlify.app](https://hovira.netlify.app/)
- **Repository:** [github.com/ATS-AI-6278/IQ-Hackathon](https://github.com/ATS-AI-6278/IQ-Hackathon)
- **Technical Documentation:** [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)

---

## Screenshots

| Dashboard | Create Passport | Scanner |
|:---------:|:---------------:|:-------:|
| ![Dashboard](docs/screenshots/home.png) | ![Create Passport](docs/screenshots/create-passport.png) | ![Scanner](docs/screenshots/scanner.png) |

| Ask Hovira | Product Scan | AI Insight | Mobile Scan |
|:----------:|:------------:|:----------:|:-----------:|
| ![Ask Hovira](docs/screenshots/ask-hovira.png) | ![Product Scan](docs/screenshots/product-scan.png) | ![AI Insight](docs/screenshots/ai-insight.png) | ![Mobile Scan](docs/screenshots/mobile-scan.png) |

> Screenshots are from the current demo. Replace with actual UI captures as the product evolves.

---

<div align="center">

**Hovira** -- From scattered papers to household intelligence.

Licensed under [Apache 2.0](LICENSE)

</div>
