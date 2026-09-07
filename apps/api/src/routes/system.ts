import { Router, type IRouter } from "express";
import { GetSystemStatusResponse } from "@workspace/api-zod";
import { getAiStatus, lanAddresses } from "../lib/ai-client";

const router: IRouter = Router();

router.get("/system/status", async (_req, res): Promise<void> => {
  const status = await getAiStatus();
  res.json(GetSystemStatusResponse.parse(status));
});

router.get("/system/lan", (_req, res): void => {
  res.json(lanAddresses());
});

export default router;