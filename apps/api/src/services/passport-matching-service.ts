import type {
  ProductIdentification,
  ProductMatchConfidence,
  ProductMatchResponse,
} from "@workspace/api-zod";
import { findBestMatches } from "../lib/passport-store";

export async function matchProduct(
  identifiedProduct: ProductIdentification,
): Promise<ProductMatchResponse> {
  const matches = findBestMatches(identifiedProduct).map((passport, index) => {
    const exactBrand =
      passport.brand.toLowerCase() === identifiedProduct.brand.toLowerCase();
    const exactModel =
      passport.model.toLowerCase() === identifiedProduct.model.toLowerCase();
    const exactSerial =
      passport.serialNumber.toLowerCase() ===
      identifiedProduct.serialNumber.toLowerCase();
    const score = index === 0 && exactModel ? 0.96 : index === 1 ? 0.63 : 0.48;
    const confidence: ProductMatchConfidence =
      score >= 0.8 ? "high" : score >= 0.6 ? "medium" : "low";
    return {
      passportId: passport.passportId,
      matchScore: score,
      confidence,
      reason: [
        ...(exactBrand ? ["Brand matches"] : []),
        ...(exactModel ? ["Model matches"] : []),
        ...(exactSerial ? ["Serial number matches"] : []),
        ...(exactBrand && !exactModel ? ["Same product category"] : []),
      ],
      passport,
    };
  });
  return { matches };
}