import { Router, type IRouter } from "express";
import {
  AnalyzeDocumentBody,
  AnalyzeDocumentResponse,
  CreatePassportBody,
  CreatePassportResponse,
  GetDashboardSummaryResponse,
  GetPassportParams,
  GetPassportResponse,
  ListPassportsQueryParams,
  ListPassportsResponse,
  PassportUpdate,
  UpdatePassportBody,
  UpdatePassportParams,
  UpdatePassportResponse,
} from "@workspace/api-zod";
import {
  createPassport,
  getPassport,
  getSummary,
  listPassports,
  updatePassport,
} from "../lib/passport-store";
import { analyzeDocument } from "../services/document-analysis-service";

const router: IRouter = Router();

router.get("/passports", (req, res): void => {
  const parsed = ListPassportsQueryParams.safeParse(req.query);
  if (!parsed.success) {
    req.log.warn({ errors: parsed.error.message }, "Invalid passport filters");
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  res.json(ListPassportsResponse.parse(listPassports(parsed.data)));
});

router.post("/passport/create", (req, res): void => {
  const parsed = CreatePassportBody.safeParse(req.body);
  if (!parsed.success) {
    req.log.warn({ errors: parsed.error.message }, "Invalid passport input");
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  res.status(201).json(CreatePassportResponse.parse(createPassport(parsed.data)));
});

router.get("/passport/:passportId", (req, res): void => {
  const params = GetPassportParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const passport = getPassport(params.data.passportId);
  if (!passport) {
    res.status(404).json({ error: "Passport not found" });
    return;
  }
  res.json(GetPassportResponse.parse(passport));
});

router.patch("/passport/:passportId", (req, res): void => {
  const params = UpdatePassportParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const parsed = UpdatePassportBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  const passport = updatePassport(params.data.passportId, parsed.data);
  if (!passport) {
    res.status(404).json({ error: "Passport not found" });
    return;
  }
  res.json(UpdatePassportResponse.parse(passport));
});

router.post("/passport/analyze-document", async (req, res): Promise<void> => {
  const parsed = AnalyzeDocumentBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  const analysis = await analyzeDocument(parsed.data);
  res.json(AnalyzeDocumentResponse.parse(analysis));
});

router.get("/dashboard/summary", (_req, res): void => {
  res.json(GetDashboardSummaryResponse.parse(getSummary()));
});

export default router;