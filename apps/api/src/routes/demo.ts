import fs from "node:fs";
import path from "node:path";
import { Router, type IRouter, type Request, type Response } from "express";

const router: IRouter = Router();

// Base directories for samples
const SAMPLES_DIR = path.resolve(process.cwd(), "samples");
const VAL_IMAGES_DIR = path.resolve(process.cwd(), "Model/dataset/images/val");

function fileToDataUrl(filePath: string, mimeType: string): string {
  if (!fs.existsSync(filePath)) return "";
  const buf = fs.readFileSync(filePath);
  return `data:${mimeType};base64,${buf.toString("base64")}`;
}

router.get("/demo-presets", (_req: Request, res: Response) => {
  try {
    const presets = [
      {
        id: "preset-washer",
        title: "Electrolux Washer",
        category: "Home appliance",
        description: "Official warranty card + front-load washing machine scan",
        docName: "Electrolux_Warranty_Card.png",
        docType: "image/png",
        docContent: fileToDataUrl(path.join(SAMPLES_DIR, "image2.png"), "image/png"),
        photoName: "Washing_Machine_Scan.png",
        photoType: "image/png",
        photoContent: fileToDataUrl(path.join(VAL_IMAGES_DIR, "1_0a9c0a67-wm3.png"), "image/png"),
      },
      {
        id: "preset-ac",
        title: "Haier Split AC",
        category: "Home appliance",
        description: "Manufacturer warranty invoice + split AC wall unit scan",
        docName: "Haier_AC_Invoice.png",
        docType: "image/png",
        docContent: fileToDataUrl(path.join(SAMPLES_DIR, "image1.png"), "image/png"),
        photoName: "Air_Conditioner_Scan.png",
        photoType: "image/png",
        photoContent: fileToDataUrl(path.join(VAL_IMAGES_DIR, "0_154ea932-c22.png"), "image/png"),
      },
      {
        id: "preset-closet",
        title: "Wardrobe / Closet",
        category: "Furniture",
        description: "Extended warranty doc + wooden almirah closet scan",
        docName: "Wardrobe_Receipt.webp",
        docType: "image/webp",
        docContent: fileToDataUrl(path.join(SAMPLES_DIR, "ocr check.webp"), "image/webp"),
        photoName: "Physical_Closet_Scan.jpg",
        photoType: "image/jpeg",
        photoContent: fileToDataUrl(path.join(SAMPLES_DIR, "img.jpg"), "image/jpeg"),
      },
      {
        id: "preset-cot",
        title: "Bedstead / Cot",
        category: "Furniture",
        description: "Purchase invoice + physical cot bed scan",
        docName: "Furniture_Invoice.png",
        docType: "image/png",
        docContent: fileToDataUrl(path.join(SAMPLES_DIR, "hi.png"), "image/png"),
        photoName: "Physical_Cot_Scan.jpg",
        photoType: "image/jpeg",
        photoContent: fileToDataUrl(path.join(SAMPLES_DIR, "img3.jpg"), "image/jpeg"),
      },
    ];

    return res.json(presets);
  } catch (err) {
    return res.status(500).json({ error: "Failed to load demo presets" });
  }
});

export default router;
