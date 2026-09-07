export type GraphNode = {
  passport: {
    passportId: string;
    product: string;
    brand: string;
    model: string;
    serialNumber: string;
    category: string;
    purchaseDate: string | null;
    purchasePrice: number | null;
    currency: string | null;
    warranty: string | null;
    seller: string | null;
    sourceDocument: string | null;
    physicalProductImage: string | null;
    verificationStatus: string;
  };
  memory: {
    passportId: string;
    roomId: string | null;
    locationNote: string;
    lastSeenAt: string | null;
    lastSeenConfidence: string;
    lifecycle: string;
    notes: string;
  };
  room: { id: string; name: string } | null;
  warrantyDaysLeft: number | null;
  ageYears: number | null;
  seal: string;
  evidence: Record<string, string>;
  missing: string[];
};

export type QuietNotice = {
  id: string;
  passportId: string | null;
  kind: string;
  title: string;
  detail: string;
  href: string;
};

export async function fetchGraph() {
  const resp = await fetch('/api/household/graph');
  if (!resp.ok) throw new Error('Graph unavailable');
  return resp.json() as Promise<{
    home: { name: string; privacy: string };
    rooms: Array<{ id: string; name: string }>;
    nodes: GraphNode[];
    byRoom: Array<{ room: { id: string; name: string }; items: GraphNode[] }>;
    timeline: Array<{ id: string; passportId: string; type: string; at: string; text: string; confidence: string }>;
  }>;
}

export async function fetchNotices() {
  const resp = await fetch('/api/household/notices');
  if (!resp.ok) return { notices: [] as QuietNotice[] };
  return resp.json() as Promise<{ notices: QuietNotice[] }>;
}

export async function fetchProductMemory(id: string) {
  const resp = await fetch(`/api/household/product/${encodeURIComponent(id)}`);
  if (!resp.ok) return null;
  return resp.json() as Promise<GraphNode>;
}

export async function placeProduct(id: string, roomId: string | null, locationNote: string) {
  const resp = await fetch(`/api/household/product/${encodeURIComponent(id)}/place`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ roomId, locationNote, confidence: 'confirmed' }),
  });
  if (!resp.ok) throw new Error('Could not place');
  return resp.json() as Promise<GraphNode>;
}

export async function fetchRooms() {
  const resp = await fetch('/api/household/rooms');
  if (!resp.ok) return { rooms: [] as Array<{ id: string; name: string }> };
  return resp.json() as Promise<{ rooms: Array<{ id: string; name: string }> }>;
}
