import type {
  ProductIdentification,
  ProductMatchConfidence,
  ProductMatchResponse,
} from "@workspace/api-zod";
import { findBestMatches } from "../lib/passport-store";

export async function matchProduct(
  identifiedProduct: ProductIdentification,
): Promise<ProductMatchResponse> {
  // If unidentified or zero confidence, return no matches
  if (
    !identifiedProduct.detectedProduct ||
    identifiedProduct.detectedProduct === "Unidentified Product" ||
    identifiedProduct.confidence === 0
  ) {
    return { matches: [] };
  }

  const idBrand = identifiedProduct.brand?.trim().toLowerCase() || "";
  const idModel = identifiedProduct.model?.trim().toLowerCase() || "";
  const idCategory = identifiedProduct.category?.trim().toLowerCase() || "";
  const idSerial = identifiedProduct.serialNumber?.trim().toLowerCase() || "";
  const idProduct = identifiedProduct.detectedProduct?.trim().toLowerCase() || "";

  const candidatePassports = findBestMatches(identifiedProduct);

  const matches = candidatePassports
    .map((passport) => {
      const pBrand = passport.brand.toLowerCase();
      const pModel = passport.model.toLowerCase();
      const pCategory = passport.category.toLowerCase();
      const pSerial = passport.serialNumber.toLowerCase();
      const pProduct = passport.product.toLowerCase();

      const reasons: string[] = [];
      let score = 0;

      if (idSerial && pSerial && idSerial === pSerial) {
        score += 0.45;
        reasons.push("Serial number matches exactly");
      }
      if (idModel && pModel && (idModel === pModel || pModel.includes(idModel) || idModel.includes(pModel))) {
        score += 0.30;
        reasons.push("Model designation matches");
      }
      if (idBrand && pBrand && (idBrand === pBrand || pBrand.includes(idBrand) || idBrand.includes(pBrand))) {
        score += 0.15;
        reasons.push("Brand matches");
      }
      if (idCategory && pCategory && (idCategory === pCategory || pCategory.includes(idCategory) || idCategory.includes(pCategory))) {
        score += 0.10;
        reasons.push("Product category matches");
      } else if (pProduct.includes(idProduct) || idProduct.includes(pProduct)) {
        score += 0.10;
        reasons.push("Product form factor matches");
      }

      // If YOLO visual classification matched category/product without model, factor in detector confidence
      if (!idBrand && !idModel && (idCategory === pCategory || pProduct.includes(idProduct))) {
        score = Math.max(score, Math.round(identifiedProduct.confidence * 0.8 * 100) / 100);
        reasons.push(`Visual classification match (${Math.round(identifiedProduct.confidence * 100)}%)`);
      }

      score = Math.min(Math.round(score * 100) / 100, 0.99);

      const confidence: ProductMatchConfidence =
        score >= 0.75 ? "high" : score >= 0.45 ? "medium" : "low";

      return {
        passportId: passport.passportId,
        matchScore: score,
        confidence,
        reason: reasons.length > 0 ? reasons : ["General product similarity"],
        passport,
      };
    })
    .filter((m) => m.matchScore > 0);

  return { matches };
}