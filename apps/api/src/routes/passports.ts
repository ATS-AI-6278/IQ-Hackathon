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
  evidenceSeal,
  getPassport,
  getSummary,
  listPassports,
  updatePassport,
} from "../lib/passport-store";
import { graphNode, onPassportCreated } from "../lib/household-graph";
import { analyzeDocument } from "../services/document-analysis-service";
import { logger } from "../lib/logger";

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
  const created = createPassport(parsed.data);
  onPassportCreated(created);
  logger.info(`📜 DPP Minted: #${created.passportId} · ${created.product} (${created.brand})`);
  res.status(201).json(CreatePassportResponse.parse(created));
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
  const firstProd = analysis.products?.[0];
  logger.info(
    `📄 Document Processed: ${firstProd?.product || parsed.data.fileName} (${firstProd?.brand || "Generic"})`,
  );
  res.json(AnalyzeDocumentResponse.parse(analysis));
});

router.get("/dashboard/summary", (_req, res): void => {
  res.json(GetDashboardSummaryResponse.parse(getSummary()));
});

router.get("/passport/:passportId/claim-pack", (req, res): void => {
  const passport = getPassport(String(req.params.passportId));
  if (!passport) {
    res.status(404).json({ error: "Passport not found" });
    return;
  }
  const node = graphNode(passport);
  res.json({
    title: `Claim pack · ${passport.product}`,
    generatedAt: new Date().toISOString(),
    seal: node.seal,
    room: node.room?.name || null,
    evidence: node.evidence,
    fields: {
      passportId: passport.passportId,
      product: passport.product,
      brand: passport.brand,
      model: passport.model,
      serialNumber: passport.serialNumber,
      purchaseDate: passport.purchaseDate,
      warranty: passport.warranty,
      seller: passport.seller,
      invoiceNumber: passport.invoiceNumber,
      verificationStatus: passport.verificationStatus,
    },
    physicalProductImage: passport.physicalProductImage,
    notes: "Only vault fields. Unknown serials stay blank.",
  });
});

router.get("/passport/:passportId/seal", (req, res): void => {
  const passport = getPassport(String(req.params.passportId));
  if (!passport) {
    res.status(404).json({ error: "Passport not found" });
    return;
  }
  res.json({ algorithm: "SHA-256", digest: evidenceSeal(passport) });
});

export default router;