import type {
  ProductIdentification,
  ProductIdentificationInput,
} from "@workspace/api-zod";
import { runProductIdentification } from "../lib/ai-client";

export async function identifyProduct(
  input: ProductIdentificationInput & { fast?: boolean },
): Promise<ProductIdentification> {
  return runProductIdentification(input);
}