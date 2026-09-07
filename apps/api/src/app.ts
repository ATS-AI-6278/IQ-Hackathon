import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import express, { type Express } from "express";
import cors from "cors";
import pinoHttp from "pino-http";
import router from "./routes";
import householdRouter from "./routes/household";
import { logger } from "./lib/logger";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app: Express = express();

app.use(
  pinoHttp({
    logger,
    autoLogging: {
      ignore: (req) => {
        const url = req.url || "";
        // Don't flood terminal with periodic webcam frames or health checks
        return (
          url.includes("/product/identify") ||
          url.includes("/product/match") ||
          url.includes("/health") ||
          url.includes("/system/status")
        );
      },
    },
    customLogLevel(req, res, err) {
      if (res.statusCode >= 500 || err) return "error";
      if (res.statusCode >= 400) return "warn";
      return "info";
    },
    customSuccessMessage(req, res) {
      return `${req.method} ${req.url?.split("?")[0]} -> ${res.statusCode}`;
    },
    customErrorMessage(req, res, err) {
      return `${req.method} ${req.url?.split("?")[0]} -> ${res.statusCode} (${err?.message || "error"})`;
    },
    serializers: {
      req: () => undefined,
      res: () => undefined,
    },
  }),
);
app.use(cors());
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" }));

// API routes
app.use("/api", router);
app.use("/api/household", householdRouter);

// Serve frontend static build if present
const webDist = path.resolve(__dirname, "../../../apps/web/dist");
if (fs.existsSync(webDist)) {
  app.use(express.static(webDist));
  app.use((req, res, next) => {
    if (req.path.startsWith("/api")) {
      return next();
    }
    res.sendFile(path.join(webDist, "index.html"));
  });
}

export default app;
