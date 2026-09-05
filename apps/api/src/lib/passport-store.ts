import type {
  Activity,
  Passport,
  PassportInput,
  ProductIdentification,
} from "@workspace/api-zod";

const now = "2026-09-03T09:30:00.000Z";

const passports: Passport[] = [
  {
    passportId: "DPP-00024",
    product: "Bespoke Refrigerator",
    brand: "Samsung",
    model: "RB34T672EWW",
    serialNumber: "0A8K91B43",
    category: "Home appliance",
    documentType: "Warranty certificate",
    purchaseDate: "2025-08-12",
    purchasePrice: 689,
    currency: "EUR",
    warranty: "24 months",
    seller: "Nordhaus Living",
    customerName: "Ava Morgan",
    orderId: "NH-48219",
    invoiceNumber: "INV-2025-1842",
    sourceDocument: "warranty-certificate.pdf",
    physicalProductImage: null,
    physicalScanDate: null,
    matchConfidence: null,
    verificationStatus: "pending",
    createdAt: "2026-08-24T10:15:00.000Z",
    updatedAt: "2026-08-24T10:15:00.000Z",
  },
  {
    passportId: "DPP-00023",
    product: "Precision Espresso Maker",
    brand: "Electrolux",
    model: "E6EC1-6ST",
    serialNumber: "ELX-7731-91",
    category: "Small domestic appliance",
    documentType: "Purchase invoice",
    purchaseDate: "2025-06-04",
    purchasePrice: 349,
    currency: "EUR",
    warranty: "12 months",
    seller: "Field & Form",
    customerName: "Ava Morgan",
    orderId: "FF-20831",
    invoiceNumber: "FF-INV-934",
    sourceDocument: "purchase-invoice.jpg",
    physicalProductImage: "scan:espresso",
    physicalScanDate: "2026-08-29T14:40:00.000Z",
    matchConfidence: 0.96,
    verificationStatus: "verified",
    createdAt: "2026-08-20T08:00:00.000Z",
    updatedAt: "2026-08-29T14:40:00.000Z",
  },
  {
    passportId: "DPP-00022",
    product: "Latitude 7440",
    brand: "Dell",
    model: "Latitude 7440",
    serialNumber: "DL-7F4K-2201",
    category: "Computing",
    documentType: "Retail receipt",
    purchaseDate: "2024-11-18",
    purchasePrice: 1249,
    currency: "USD",
    warranty: "36 months",
    seller: "Northstar Office",
    customerName: "Ava Morgan",
    orderId: "NS-11028",
    invoiceNumber: null,
    sourceDocument: "receipt.png",
    physicalProductImage: "scan:laptop",
    physicalScanDate: "2026-08-27T11:20:00.000Z",
    matchConfidence: 0.91,
    verificationStatus: "verified",
    createdAt: "2026-08-18T11:30:00.000Z",
    updatedAt: "2026-08-27T11:20:00.000Z",
  },
  {
    passportId: "DPP-00021",
    product: "iPhone 15 Pro",
    brand: "Apple",
    model: "A2848",
    serialNumber: "F2LQ3T1N8P",
    category: "Mobile device",
    documentType: "Order confirmation",
    purchaseDate: "2024-02-02",
    purchasePrice: 999,
    currency: "USD",
    warranty: "12 months",
    seller: "Apple Store",
    customerName: "Ava Morgan",
    orderId: "W123456789",
    invoiceNumber: "APL-88402",
    sourceDocument: "order-confirmation.pdf",
    physicalProductImage: "scan:phone",
    physicalScanDate: "2026-08-25T16:05:00.000Z",
    matchConfidence: 0.99,
    verificationStatus: "verified",
    createdAt: "2026-08-12T09:05:00.000Z",
    updatedAt: "2026-08-25T16:05:00.000Z",
  },
  {
    passportId: "DPP-00020",
    product: "Series 5000 Washing Machine",
    brand: "LG",
    model: "F4V5VYP2T",
    serialNumber: "LG-5P01-4928",
    category: "Home appliance",
    documentType: "Warranty card",
    purchaseDate: "2025-03-22",
    purchasePrice: 749,
    currency: "GBP",
    warranty: "24 months",
    seller: "Household & Co.",
    customerName: "Ava Morgan",
    orderId: "HC-77821",
    invoiceNumber: "HC-55219",
    sourceDocument: "warranty-card.jpg",
    physicalProductImage: null,
    physicalScanDate: null,
    matchConfidence: null,
    verificationStatus: "pending",
    createdAt: "2026-08-05T13:20:00.000Z",
    updatedAt: "2026-08-05T13:20:00.000Z",
  },
];

const activity: Activity[] = [
  {
    id: "act-001",
    type: "linked",
    title: "Physical product linked",
    description: "iPhone 15 Pro was linked to Passport DPP-00021",
    timestamp: "2026-09-03T08:42:00.000Z",
    passportId: "DPP-00021",
  },
  {
    id: "act-002",
    type: "scanned",
    title: "Product scan completed",
    description: "A Latitude 7440 was identified with 91% confidence",
    timestamp: "2026-09-02T11:20:00.000Z",
    passportId: "DPP-00022",
  },
  {
    id: "act-003",
    type: "created",
    title: "New passport created",
    description: "Precision Espresso Maker added from purchase invoice",
    timestamp: "2026-08-29T14:40:00.000Z",
    passportId: "DPP-00023",
  },
  {
    id: "act-004",
    type: "analyzed",
    title: "Warranty document processed",
    description: "Warranty card analyzed and product identity extracted",
    timestamp: "2026-08-24T10:15:00.000Z",
    passportId: "DPP-00024",
  },
];

export function listPassports(filters: {
  search?: string;
  category?: string;
  status?: string;
}): Passport[] {
  const search = filters.search?.trim().toLowerCase();
  return passports.filter((passport) => {
    const matchesSearch =
      !search ||
      [
        passport.product,
        passport.brand,
        passport.model,
        passport.serialNumber,
        passport.category,
      ].some((value) => value.toLowerCase().includes(search));
    const matchesCategory =
      !filters.category || passport.category === filters.category;
    const matchesStatus =
      !filters.status || passport.verificationStatus === filters.status;
    return matchesSearch && matchesCategory && matchesStatus;
  });
}

export function getPassport(passportId: string): Passport | undefined {
  return passports.find((passport) => passport.passportId === passportId);
}

export function createPassport(input: PassportInput): Passport {
  const passport: Passport = {
    ...input,
    passportId: `DPP-${String(passports.length + 20).padStart(5, "0")}`,
    physicalProductImage: null,
    physicalScanDate: null,
    matchConfidence: null,
    verificationStatus: "pending",
    createdAt: now,
    updatedAt: now,
  };
  passports.unshift(passport);
  activity.unshift({
    id: `act-${String(activity.length + 1).padStart(3, "0")}`,
    type: "created",
    title: "New passport created",
    description: `${passport.product} was added from ${passport.documentType.toLowerCase()}`,
    timestamp: now,
    passportId: passport.passportId,
  });
  return passport;
}

export function updatePassport(
  passportId: string,
  updates: Partial<PassportInput>,
): Passport | undefined {
  const passport = getPassport(passportId);
  if (!passport) return undefined;
  Object.assign(passport, updates, { updatedAt: now });
  return passport;
}

export function linkProduct(
  passportId: string,
  image: string,
  confidence: number,
  scanDate: string,
): Passport | undefined {
  const passport = getPassport(passportId);
  if (!passport) return undefined;
  Object.assign(passport, {
    physicalProductImage: image,
    physicalScanDate: scanDate,
    matchConfidence: confidence,
    verificationStatus: "verified",
    updatedAt: scanDate,
  });
  activity.unshift({
    id: `act-${String(activity.length + 1).padStart(3, "0")}`,
    type: "linked",
    title: "Product successfully linked",
    description: `${passport.product} is now physically verified`,
    timestamp: scanDate,
    passportId,
  });
  return passport;
}

export function listActivity(): Activity[] {
  return activity;
}

export function getSummary() {
  return {
    totalPassports: passports.length,
    productsScanned: passports.filter((passport) => passport.physicalProductImage)
      .length,
    documentsProcessed: passports.length + 7,
    successfullyLinked: passports.filter(
      (passport) => passport.verificationStatus === "verified",
    ).length,
  };
}

export function findBestMatches(
  identified: ProductIdentification,
): Passport[] {
  if (
    !identified.detectedProduct ||
    identified.detectedProduct === "Unidentified Product" ||
    identified.confidence === 0
  ) {
    return [];
  }

  const idBrand = identified.brand?.trim().toLowerCase() || "";
  const idModel = identified.model?.trim().toLowerCase() || "";
  const idCategory = identified.category?.trim().toLowerCase() || "";
  const idSerial = identified.serialNumber?.trim().toLowerCase() || "";
  const idProduct = identified.detectedProduct?.trim().toLowerCase() || "";

  const ranked = passports
    .map((passport) => {
      let score = 0;
      const pBrand = passport.brand.toLowerCase();
      const pModel = passport.model.toLowerCase();
      const pCategory = passport.category.toLowerCase();
      const pSerial = passport.serialNumber.toLowerCase();
      const pProduct = passport.product.toLowerCase();

      if (idSerial && pSerial && idSerial === pSerial) {
        score += 0.45;
      }
      if (idModel && pModel && (idModel === pModel || pModel.includes(idModel) || idModel.includes(pModel))) {
        score += 0.30;
      }
      if (idBrand && pBrand && (idBrand === pBrand || pBrand.includes(idBrand) || idBrand.includes(pBrand))) {
        score += 0.15;
      }
      if (idCategory && pCategory && (idCategory === pCategory || pCategory.includes(idCategory) || idCategory.includes(pCategory))) {
        score += 0.10;
      } else if (pProduct.includes(idProduct) || idProduct.includes(pProduct)) {
        score += 0.10;
      }

      // If YOLO visual classification matched category/product without model, factor in detector confidence
      if (!idBrand && !idModel && (idCategory === pCategory || pProduct.includes(idProduct))) {
        score = Math.max(score, Math.round(identified.confidence * 0.8 * 100) / 100);
      }

      return { passport, score: Math.min(score, 0.99) };
    })
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score);

  return ranked.slice(0, 3).map(({ passport }) => passport);
}