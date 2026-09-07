import os from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import type {
  DocumentAnalysis,
  DocumentAnalysisInput,
  ProductIdentification,
  ProductIdentificationInput,
  SystemStatus,
} from "@workspace/api-zod";
import { logger } from "./logger";

const AI_SERVICE_URL = process.env["AI_SERVICE_URL"] || "http://127.0.0.1:8000";
const PYTHON_CMD = process.env["PYTHON_PATH"] || "python";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const AI_SERVICE_DIR = path.resolve(__dirname, "../../../ai-service");

const EMPTY_ANALYSIS: DocumentAnalysis = {
  documentType: "Other",
  products: [
    {
      product: "Unverified document",
      brand: "",
      model: "",
      serialNumber: "",
      category: "Other",
      selected: true,
      evidence: "Local AI service unavailable. No fields were invented.",
    },
  ],
  extractedFields: {
    purchaseDate: null,
    purchasePrice: null,
    currency: null,
    warranty: null,
    seller: null,
  },
};

const EMPTY_IDENTIFY: ProductIdentification = {
  detectedProduct: "Unidentified Product",
  category: "Other",
  brand: "",
  model: "",
  serialNumber: "",
  confidence: 0,
  boundingBox: [],
  visualFeatures: ["Local AI service unavailable. Nothing was invented."],
};

async function runPythonCli(command: string, inputPayload?: unknown): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const proc = spawn(PYTHON_CMD, ["-m", "app.runner", command], {
      cwd: AI_SERVICE_DIR,
      stdio: ["pipe", "pipe", "pipe"],
      windowsHide: true,
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    proc.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    proc.on("error", reject);
    proc.on("close", (code) => {
      if (code !== 0) {
        return reject(new Error(`Python runner exited with code ${code}: ${stderr}`));
      }
      try {
        resolve(JSON.parse(stdout.trim()));
      } catch (e) {
        reject(new Error(`Failed to parse Python output: ${stdout}. Error: ${e}`));
      }
    });

    if (inputPayload !== undefined) {
      proc.stdin.write(JSON.stringify(inputPayload));
      proc.stdin.end();
    } else {
      proc.stdin.end();
    }
  });
}

export function lanAddresses(): { urls: string[]; preferred: string } {
  const port = process.env["WEB_PORT"] || "5173";
  const urls: string[] = [];
  const nets = os.networkInterfaces();
  for (const entries of Object.values(nets)) {
    for (const entry of entries || []) {
      if (entry.family === "IPv4" && !entry.internal) {
        urls.push(`http://${entry.address}:${port}/camera`);
      }
    }
  }
  return { urls, preferred: urls[0] || `http://127.0.0.1:${port}/scan` };
}

export async function getAiStatus(): Promise<SystemStatus> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const resp = await fetch(`${AI_SERVICE_URL}/status`, { signal: controller.signal });
    clearTimeout(timeoutId);
    if (resp.ok) {
      const remote = (await resp.json()) as SystemStatus;
      return {
        backend: {
          name: "Passport API",
          status: "connected",
          detail: "SQLite-style JSON vault · Express 5",
        },
        services: remote.services || [],
      };
    }
  } catch (_e) {
    // try CLI
  }

  try {
    const cliRes = (await runPythonCli("status")) as SystemStatus;
    if (cliRes?.services) {
      return {
        backend: {
          name: "Passport API",
          status: "connected",
          detail: "Vault ready · AI via CLI bridge",
        },
        services: cliRes.services,
      };
    }
  } catch (_e) {
    // honest offline
  }

  return {
    backend: {
      name: "Passport API",
      status: "connected",
      detail: "API up · Python AI engine unreachable",
    },
    services: [
      { name: "OCR engine", status: "unavailable", detail: "Start pnpm dev:ai (port 8000)" },
      { name: "Vision model", status: "unavailable", detail: "Qwen2.5-VL via Ollama not reachable" },
      { name: "Household LLM", status: "unavailable", detail: "Gemma 2 via Ollama not reachable" },
      { name: "Product detection", status: "unavailable", detail: "YOLO service offline" },
    ],
  };
}

export async function runDocumentAnalysis(
  input: DocumentAnalysisInput,
): Promise<DocumentAnalysis> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 90000);
    const resp = await fetch(`${AI_SERVICE_URL}/analyze-document`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (resp.ok) {
      return (await resp.json()) as DocumentAnalysis;
    }
  } catch (e) {
    logger.warn({ err: e }, "HTTP analyze-document failed, trying Python CLI fallback");
  }

  try {
    const cliResult = (await runPythonCli("analyze", input)) as DocumentAnalysis;
    if (cliResult?.products?.length) {
      return cliResult;
    }
  } catch (e) {
    logger.warn({ err: e }, "Python CLI runner failed");
  }

  return EMPTY_ANALYSIS;
}

export async function runProductIdentification(
  input: ProductIdentificationInput & { fast?: boolean },
): Promise<ProductIdentification> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), input.fast ? 8000 : 45000);
    const resp = await fetch(`${AI_SERVICE_URL}/identify-product`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: input.image, fast: Boolean(input.fast) }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (resp.ok) {
      return (await resp.json()) as ProductIdentification;
    }
  } catch (e) {
    logger.warn({ err: e }, "HTTP identify-product failed, trying Python CLI fallback");
  }

  try {
    const cliResult = (await runPythonCli("identify", input)) as ProductIdentification;
    if (cliResult?.detectedProduct) {
      return cliResult;
    }
  } catch (e) {
    logger.warn({ err: e }, "Python CLI identify runner failed");
  }

  return EMPTY_IDENTIFY;
}

export async function runHouseholdAsk(question: string, passports: unknown[]): Promise<Record<string, unknown>> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);
    const resp = await fetch(`${AI_SERVICE_URL}/ask-household`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, passports }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (resp.ok) {
      return (await resp.json()) as Record<string, unknown>;
    }
  } catch (e) {
    logger.warn({ err: e }, "HTTP ask-household failed, trying CLI");
  }

  try {
    return (await runPythonCli("ask", { question, passports })) as Record<string, unknown>;
  } catch (e) {
    logger.warn({ err: e }, "Household ask unavailable");
    return {
      answer: "Household LLM is offline. I can still list passports from the local vault once the AI service is running.",
      why: "Ollama Gemma / Python engine not reachable.",
      sources: [],
      confidence: 0.4,
      intent: "none",
      engine: "offline",
    };
  }
}
