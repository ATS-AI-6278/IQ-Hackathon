import { Router, type IRouter } from "express";
import {
  IdentifyProductBody,
  IdentifyProductResponse,
  LinkProductBody,
  LinkProductParams,
  LinkProductResponse,
  MatchProductBody,
  MatchProductResponse,
  type ProductIdentification,
} from "@workspace/api-zod";
import { linkProduct, getPassport } from "../lib/passport-store";
import { markSeen } from "../lib/household-graph";
import { identifyProduct } from "../services/product-identification-service";
import { matchProduct } from "../services/passport-matching-service";
import { logger } from "../lib/logger";

const router: IRouter = Router();

router.post("/product/identify", async (req, res): Promise<void> => {
  const parsed = IdentifyProductBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  const result = await identifyProduct({
    ...parsed.data,
    fast: Boolean((req.body as { fast?: boolean })?.fast),
  });
  if (
    result.detectedProduct &&
    result.detectedProduct !== "Unidentified Product" &&
    (result.confidence || 0) > 0.2
  ) {
    logger.info(
      `🎯 Detected: ${result.detectedProduct} (${Math.round((result.confidence || 0) * 100)}% conf)`,
    );
  }
  const parsedOut = IdentifyProductResponse.parse(result);
  const extra = result as ProductIdentification & { source?: string; mode?: string; yoloHint?: string };
  res.json({
    ...parsedOut,
    source: extra.source,
    mode: extra.mode,
    yoloHint: extra.yoloHint,
  });
});

router.post("/product/match", async (req, res): Promise<void> => {
  const parsed = MatchProductBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  const result = await matchProduct(parsed.data.detectedProduct);
  if (result.matches && result.matches.length > 0) {
    const firstMatch = result.matches[0];
    logger.info(
      `🔗 Matched: ${firstMatch.passport.product} (${firstMatch.confidence} conf, ${result.matches.length} match(es))`,
    );
  }
  res.json(MatchProductResponse.parse(result));
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
  markSeen(params.data.passportId, "confirmed");
  res.json(LinkProductResponse.parse(passport));
});

export default router;