import type {
  ProductIdentification,
  ProductMatchConfidence,
  ProductMatchResponse,
} from "@workspace/api-zod";
import { findBestMatches } from "../lib/passport-store";

const PRODUCT_ALIASES: Record<string, string[]> = {
  washer: ["washing machine", "washer", "front load", "top load", "laundry", "washer-dryer"],
  ac: ["air conditioner", "ac", "split ac", "inverter ac", "cooler", "hvac"],
  purifier: ["water purifier", "water filter", "ro purifier", "uv purifier", "aquaguard", "pureit", "kent", "filter"],
  closet: ["closet", "wardrobe", "cupboard", "almirah", "armoire", "cabinet"],
  cot: ["cot", "bed", "mattress", "bedstead", "bunk"],
  refrigerator: ["refrigerator", "fridge", "freezer", "deep freezer"],
  tv: ["television", "tv", "smart tv", "display", "monitor"],
  laptop: ["laptop", "notebook", "macbook", "thinkpad", "computer"],
  microwave: ["microwave", "oven", "microwave oven", "otg"],
};

function matchesAlias(strA: string, strB: string): boolean {
  const a = strA.toLowerCase();
  const b = strB.toLowerCase();
  if (a.includes(b) || b.includes(a)) return true;
  for (const group of Object.values(PRODUCT_ALIASES)) {
    const aMatch = group.some((term) => a.includes(term));
    const bMatch = group.some((term) => b.includes(term));
    if (aMatch && bMatch) return true;
  }
  return false;
}

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

      const categoryMatches = Boolean(
        idCategory && pCategory && (idCategory === pCategory || pCategory.includes(idCategory) || idCategory.includes(pCategory))
      );
      const formFactorMatches = matchesAlias(idProduct, pProduct);

      if (categoryMatches) {
        score += 0.10;
        reasons.push("Product category matches");
      }
      if (formFactorMatches) {
        score += 0.15;
        reasons.push(`Product form factor matches (${identifiedProduct.detectedProduct})`);
      }

      // If YOLO visual classification matched category/product without model, factor in detector confidence
      if (!idBrand && !idModel && (categoryMatches || formFactorMatches)) {
        score = Math.max(score, Math.round(identifiedProduct.confidence * 0.85 * 100) / 100);
        reasons.push(`Visual AI verification match (${Math.round(identifiedProduct.confidence * 100)}%)`);
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