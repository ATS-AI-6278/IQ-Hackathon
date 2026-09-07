import fs from "node:fs";
import path from "node:path";
import type { Passport } from "@workspace/api-zod";
import { evidenceSeal, getPassport, listAllPassports, warrantyDaysLeft } from "./passport-store";

export type LocationConfidence = "confirmed" | "inferred" | "uncertain";

export type Room = { id: string; name: string };

export type MemoryEvent = {
  id: string;
  passportId: string;
  type: "purchased" | "registered" | "seen" | "moved" | "serviced" | "noted" | "document_added" | "retired";
  at: string;
  text: string;
  confidence: LocationConfidence;
};

export type ProductMemory = {
  passportId: string;
  roomId: string | null;
  locationNote: string;
  lastSeenAt: string | null;
  lastSeenConfidence: LocationConfidence;
  lifecycle: "purchased" | "registered" | "in_use" | "serviced" | "moved" | "retired";
  notes: string;
};

export type QuietNotice = {
  id: string;
  passportId: string | null;
  kind: "warranty" | "missing_photo" | "missing_invoice" | "duplicate" | "serial" | "service" | "moved";
  title: string;
  detail: string;
  href: string;
};

const rooms: Room[] = [
  { id: "kitchen", name: "Kitchen" },
  { id: "laundry", name: "Laundry" },
  { id: "living", name: "Living room" },
  { id: "office", name: "Home office" },
  { id: "bedroom", name: "Bedroom" },
  { id: "unplaced", name: "Not placed yet" },
];

const memoryById: Record<string, ProductMemory> = {};
const events: MemoryEvent[] = [];

const SEED_PLACEMENT: Record<string, { roomId: string; note: string; lifecycle: ProductMemory["lifecycle"] }> = {
  "DPP-00024": { roomId: "kitchen", note: "Along the back wall", lifecycle: "in_use" },
  "DPP-00023": { roomId: "kitchen", note: "Counter, left of the sink", lifecycle: "in_use" },
  "DPP-00022": { roomId: "office", note: "Last seen near the desk", lifecycle: "in_use" },
  "DPP-00021": { roomId: "bedroom", note: "Usually on the nightstand", lifecycle: "in_use" },
  "DPP-00020": { roomId: "laundry", note: "Utility closet", lifecycle: "registered" },
};

function isoNow(): string {
  return new Date().toISOString();
}

function ensureMemory(passportId: string): ProductMemory {
  if (!memoryById[passportId]) {
    const seed = SEED_PLACEMENT[passportId];
    memoryById[passportId] = {
      passportId,
      roomId: seed?.roomId ?? null,
      locationNote: seed?.note ?? "",
      lastSeenAt: seed ? isoNow() : null,
      lastSeenConfidence: seed ? "inferred" : "uncertain",
      lifecycle: seed?.lifecycle ?? "registered",
      notes: "",
    };
  }
  return memoryById[passportId];
}

export function hydrateGraphFromPassports(): void {
  for (const passport of listAllPassports()) {
    ensureMemory(passport.passportId);
  }
}

hydrateGraphFromPassports();

const GRAPH_PATH = path.resolve(process.cwd(), "data", "household-graph.json");

function persistGraph(): void {
  try {
    fs.mkdirSync(path.dirname(GRAPH_PATH), { recursive: true });
    fs.writeFileSync(GRAPH_PATH, JSON.stringify({ memoryById, events }, null, 2), "utf8");
  } catch {
    // best-effort
  }
}

function restoreGraph(): void {
  try {
    if (!fs.existsSync(GRAPH_PATH)) return;
    const parsed = JSON.parse(fs.readFileSync(GRAPH_PATH, "utf8")) as {
      memoryById?: Record<string, ProductMemory>;
      events?: MemoryEvent[];
    };
    restoreGraphState(parsed);
  } catch {
    // keep seed
  }
}

restoreGraph();

export function listRooms(): Room[] {
  return rooms;
}

export function getRoom(id: string | null): Room | null {
  if (!id) return rooms.find((room) => room.id === "unplaced") || null;
  return rooms.find((room) => room.id === id) || null;
}

export function listEvents(passportId?: string): MemoryEvent[] {
  const rows = passportId ? events.filter((event) => event.passportId === passportId) : events;
  return [...rows].sort((a, b) => b.at.localeCompare(a.at));
}

export function addMemoryEvent(
  passportId: string,
  type: MemoryEvent["type"],
  text: string,
  confidence: LocationConfidence = "confirmed",
): MemoryEvent {
  const event: MemoryEvent = {
    id: `evt-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`,
    passportId,
    type,
    at: isoNow(),
    text,
    confidence,
  };
  events.unshift(event);
  if (events.length > 200) events.length = 200;
  persistGraph();
  return event;
}

export function placeProduct(
  passportId: string,
  roomId: string | null,
  locationNote?: string,
  confidence: LocationConfidence = "confirmed",
): ProductMemory | null {
  if (!getPassport(passportId)) return null;
  const memory = ensureMemory(passportId);
  const previousRoom = memory.roomId;
  memory.roomId = roomId;
  if (locationNote !== undefined) memory.locationNote = locationNote;
  memory.lastSeenAt = isoNow();
  memory.lastSeenConfidence = confidence;
  if (previousRoom && roomId && previousRoom !== roomId) {
    memory.lifecycle = "moved";
    addMemoryEvent(
      passportId,
      "moved",
      `Moved from ${getRoom(previousRoom)?.name || "unknown"} to ${getRoom(roomId)?.name || "unknown"}`,
      confidence,
    );
  } else {
    addMemoryEvent(passportId, "seen", `Seen in ${getRoom(roomId)?.name || "the home"}${memory.locationNote ? ` — ${memory.locationNote}` : ""}`, confidence);
  }
  persistGraph();
  return memory;
}

export function noteProduct(passportId: string, notes: string): ProductMemory | null {
  if (!getPassport(passportId)) return null;
  const memory = ensureMemory(passportId);
  memory.notes = notes;
  addMemoryEvent(passportId, "noted", notes || "Note updated", "confirmed");
  persistGraph();
  return memory;
}

export function markSeen(passportId: string, confidence: LocationConfidence = "inferred"): void {
  const memory = ensureMemory(passportId);
  memory.lastSeenAt = isoNow();
  memory.lastSeenConfidence = confidence;
  if (memory.lifecycle === "registered" || memory.lifecycle === "purchased") {
    memory.lifecycle = "in_use";
  }
  addMemoryEvent(passportId, "seen", "Recognized by camera", confidence);
}

export function onPassportCreated(passport: Passport): void {
  ensureMemory(passport.passportId);
  addMemoryEvent(passport.passportId, "registered", `${passport.product} remembered from ${passport.documentType}`, "confirmed");
  persistGraph();
}

export function fieldEvidence(passport: Passport): Record<string, string> {
  const hasPhoto = Boolean(passport.physicalProductImage);
  const hasDoc = Boolean(passport.sourceDocument);
  const serial = passport.serialNumber
    ? hasPhoto && hasDoc
      ? "Verified from document and camera"
      : hasDoc
        ? "From document OCR"
        : "Entered or extracted — confirm"
    : "Unknown";
  return {
    serial,
    model: passport.model ? (hasDoc ? "From document" : "From record") : "Unknown",
    warranty: passport.purchaseDate && passport.warranty ? "Derived from purchase date + stated duration" : "Incomplete",
    location: memoryById[passport.passportId]?.lastSeenConfidence || "uncertain",
  };
}

export function productAgeYears(passport: Passport): number | null {
  if (!passport.purchaseDate) return null;
  const start = new Date(passport.purchaseDate);
  if (Number.isNaN(start.getTime())) return null;
  return Math.max(0, (Date.now() - start.getTime()) / (365.25 * 86_400_000));
}

export type GraphNode = {
  passport: Passport;
  memory: ProductMemory;
  room: Room | null;
  warrantyDaysLeft: number | null;
  ageYears: number | null;
  seal: string;
  evidence: Record<string, string>;
  missing: string[];
};

function missingFields(passport: Passport, memory: ProductMemory): string[] {
  const missing: string[] = [];
  if (!passport.serialNumber) missing.push("serial");
  if (!passport.purchaseDate) missing.push("purchase date");
  if (!passport.sourceDocument) missing.push("invoice");
  if (!passport.physicalProductImage) missing.push("photo");
  if (!memory.roomId) missing.push("room");
  return missing;
}

export function graphNode(passport: Passport): GraphNode {
  const memory = ensureMemory(passport.passportId);
  return {
    passport,
    memory,
    room: getRoom(memory.roomId),
    warrantyDaysLeft: warrantyDaysLeft(passport),
    ageYears: productAgeYears(passport),
    seal: evidenceSeal(passport),
    evidence: fieldEvidence(passport),
    missing: missingFields(passport, memory),
  };
}

export function householdGraph() {
  const nodes = listAllPassports().map(graphNode);
  const byRoom = rooms.map((room) => ({
    room,
    items: nodes.filter((node) => (node.memory.roomId || "unplaced") === room.id),
  })).filter((group) => group.room.id === "unplaced" || group.items.length > 0 || group.room.id !== "unplaced");

  return {
    home: { name: "Home", privacy: "Local vault on this machine. Vision and Ask run locally." },
    rooms,
    nodes,
    byRoom,
    timeline: listEvents().slice(0, 20),
  };
}

export function quietNotices(): QuietNotice[] {
  const nodes = listAllPassports().map(graphNode);
  const notices: QuietNotice[] = [];

  for (const node of nodes) {
    if (node.warrantyDaysLeft !== null && node.warrantyDaysLeft <= 45) {
      notices.push({
        id: `w-${node.passport.passportId}`,
        passportId: node.passport.passportId,
        kind: "warranty",
        title: `${node.passport.product}`,
        detail:
          node.warrantyDaysLeft >= 0
            ? `Warranty ends in ${node.warrantyDaysLeft} days.`
            : `Warranty ended ${Math.abs(node.warrantyDaysLeft)} days ago.`,
        href: `/memory/${node.passport.passportId}`,
      });
    }
    if (!node.passport.physicalProductImage) {
      notices.push({
        id: `p-${node.passport.passportId}`,
        passportId: node.passport.passportId,
        kind: "missing_photo",
        title: `${node.passport.product}`,
        detail: "Remembered from paper, not yet seen by camera.",
        href: `/camera`,
      });
    }
    if (!node.passport.sourceDocument) {
      notices.push({
        id: `d-${node.passport.passportId}`,
        passportId: node.passport.passportId,
        kind: "missing_invoice",
        title: `${node.passport.product}`,
        detail: "No invoice is attached yet.",
        href: `/remember`,
      });
    }
    if (!node.passport.serialNumber) {
      notices.push({
        id: `s-${node.passport.passportId}`,
        passportId: node.passport.passportId,
        kind: "serial",
        title: `${node.passport.product}`,
        detail: "Serial is unknown. Confirm before a claim.",
        href: `/memory/${node.passport.passportId}`,
      });
    }
  }

  const models = new Map<string, GraphNode[]>();
  for (const node of nodes) {
    const key = `${node.passport.brand}|${node.passport.model}`.toLowerCase();
    if (!node.passport.model) continue;
    const list = models.get(key) || [];
    list.push(node);
    models.set(key, list);
  }
  for (const [, group] of models) {
    if (group.length < 2) continue;
    notices.push({
      id: `dup-${group[0].passport.model}`,
      passportId: group[0].passport.passportId,
      kind: "duplicate",
      title: `Two ${group[0].passport.brand} ${group[0].passport.model}`,
      detail: "Similar model numbers in this home. Confirm they are distinct machines.",
      href: `/memory`,
    });
  }

  const rank = { warranty: 0, serial: 1, missing_invoice: 2, missing_photo: 3, duplicate: 4, service: 5, moved: 6 };
  notices.sort((a, b) => rank[a.kind] - rank[b.kind]);
  return notices.slice(0, 8);
}

export function compactGraphForAsk() {
  return listAllPassports().map((passport) => {
    const node = graphNode(passport);
    return {
      passportId: passport.passportId,
      product: passport.product,
      brand: passport.brand,
      model: passport.model,
      serialNumber: passport.serialNumber,
      category: passport.category,
      purchaseDate: passport.purchaseDate,
      purchasePrice: passport.purchasePrice,
      currency: passport.currency,
      warranty: passport.warranty,
      warrantyDaysLeft: node.warrantyDaysLeft,
      seller: passport.seller,
      invoiceNumber: passport.invoiceNumber,
      sourceDocument: passport.sourceDocument,
      verificationStatus: passport.verificationStatus,
      room: node.room?.name || "Not placed yet",
      locationNote: node.memory.locationNote,
      lastSeenAt: node.memory.lastSeenAt,
      lastSeenConfidence: node.memory.lastSeenConfidence,
      lifecycle: node.memory.lifecycle,
      ageYears: node.ageYears,
      missing: node.missing,
      notes: node.memory.notes,
    };
  });
}

export function serializeGraphState() {
  return { memoryById, events };
}

export function restoreGraphState(state: { memoryById?: Record<string, ProductMemory>; events?: MemoryEvent[] }): void {
  if (state.memoryById) Object.assign(memoryById, state.memoryById);
  if (state.events?.length) {
    events.splice(0, events.length, ...state.events);
  }
}
