import { Router, type IRouter } from "express";
import {
  IdentifyProductBody,
  IdentifyProductResponse,
  LinkProductBody,
  LinkProductParams,
  LinkProductResponse,
  MatchProductBody,
  MatchProductResponse,
} from "@workspace/api-zod";
import { linkProduct, getPassport } from "../lib/passport-store";
import { identifyProduct } from "../services/product-identification-service";
import { matchProduct } from "../services/passport-matching-service";

const router: IRouter = Router();

router.post("/product/identify", async (req, res): Promise<void> => {
  const parsed = IdentifyProductBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  res.json(IdentifyProductResponse.parse(await identifyProduct(parsed.data)));
});

router.post("/product/match", async (req, res): Promise<void> => {
  const parsed = MatchProductBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  res.json(MatchProductResponse.parse(await matchProduct(parsed.data.detectedProduct)));
});

router.post(
  ["/passports/:passportId/link-product", "/passport/:passportId/link-product"],
  (req, res): void => {
  const params = LinkProductParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const parsed = LinkProductBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  if (!getPassport(params.data.passportId)) {
    res.status(404).json({ error: "Passport not found" });
    return;
  }
  const passport = linkProduct(
    params.data.passportId,
    parsed.data.image,
    parsed.data.confidence,
    parsed.data.scanDate ?? new Date().toISOString(),
  );
  res.json(LinkProductResponse.parse(passport));
});

export default router;