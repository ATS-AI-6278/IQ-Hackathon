export interface HouseholdAskResult {
  answer: string;
  why?: string;
  sources?: Array<{ passportId?: string; field?: string; label?: string }>;
  confidence?: number;
  intent?: string;
  passportId?: string;
  engine?: string;
  gemmaModel?: string;
}

export async function askHousehold(question: string): Promise<HouseholdAskResult> {
  const resp = await fetch('/api/household/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!resp.ok) {
    throw new Error('Household ask failed');
  }
  return resp.json();
}

export async function fetchInsights() {
  const resp = await fetch('/api/household/insights');
  if (!resp.ok) return null;
  return resp.json() as Promise<{
    urgent: Array<{ passportId: string; product: string; daysLeft: number | null }>;
    activeWarranties: number;
    pending: number;
    healthyCount: number;
  }>;
}

export async function fetchClaimPack(passportId: string) {
  const resp = await fetch(`/api/passport/${encodeURIComponent(passportId)}/claim-pack`);
  if (!resp.ok) throw new Error('Claim pack unavailable');
  return resp.json();
}

export async function fetchSeal(passportId: string) {
  const resp = await fetch(`/api/passport/${encodeURIComponent(passportId)}/seal`);
  if (!resp.ok) return { algorithm: 'SHA-256', digest: '' };
  return resp.json() as Promise<{ algorithm: string; digest: string }>;
}

export async function fetchLan(): Promise<{ urls: string[]; preferred: string }> {
  const resp = await fetch('/api/system/lan');
  if (!resp.ok) {
    return { urls: [], preferred: `${window.location.origin}/scan` };
  }
  return resp.json();
}

export function captureVideoFrame(video: HTMLVideoElement, maxDim = 480): string {
  const scale = maxDim / Math.max(video.videoWidth || 1, video.videoHeight || 1);
  const width = Math.max(1, Math.round((video.videoWidth || maxDim) * Math.min(1, scale)));
  const height = Math.max(1, Math.round((video.videoHeight || maxDim) * Math.min(1, scale)));
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (!ctx) return '';
  ctx.drawImage(video, 0, 0, width, height);
  return canvas.toDataURL('image/jpeg', 0.72);
}
