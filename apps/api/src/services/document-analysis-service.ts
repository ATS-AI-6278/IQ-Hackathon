import type { DocumentAnalysis, DocumentAnalysisInput } from "@workspace/api-zod";
import { runDocumentAnalysis } from "../lib/ai-client";

export async function analyzeDocument(
  input: DocumentAnalysisInput,
): Promise<DocumentAnalysis> {
  return runDocumentAnalysis(input);
}