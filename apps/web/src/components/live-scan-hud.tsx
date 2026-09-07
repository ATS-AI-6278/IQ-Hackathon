import { useEffect, useRef, useState } from 'react';
import { Camera, LoaderCircle, Sparkles, Square } from 'lucide-react';
import { captureVideoFrame } from '@/lib/household';
import type { ProductIdentification } from '@workspace/api-client-react';

interface LiveScanHudProps {
  onIdentify: (image: string, fast: boolean) => Promise<ProductIdentification | null>;
}

export function LiveScanHud({ onIdentify }: LiveScanHudProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const busyRef = useRef(false);
  const votesRef = useRef<string[]>([]);
  const [running, setRunning] = useState(false);
  const [busy, setBusy] = useState(false);
  const [qwenBusy, setQwenBusy] = useState(false);
  const [error, setError] = useState('');
  const [overlay, setOverlay] = useState<ProductIdentification | null>(null);
  const [engine, setEngine] = useState('YOLO');

  const stop = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    votesRef.current = [];
    setRunning(false);
  };

  const start = async () => {
    setError('');
    setOverlay(null);
    votesRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setRunning(true);
    } catch {
      setError('Camera permission was denied. Use upload instead.');
    }
  };

  useEffect(() => {
    if (!running) return;
    const timer = window.setInterval(async () => {
      if (busyRef.current || qwenBusy || !videoRef.current) return;
      const frame = captureVideoFrame(videoRef.current, 480);
      if (!frame) return;
      busyRef.current = true;
      setBusy(true);
      try {
        const result = await onIdentify(frame, true);
        const name = result?.detectedProduct || '';
        const ok = Boolean(result && result.confidence >= 0.5 && name && name !== 'Unidentified Product');
        if (ok && result) {
          votesRef.current = [...votesRef.current, name].slice(-4);
          const agree = votesRef.current.filter((vote) => vote === name).length;
          if (agree >= 2) {
            setOverlay(result);
            setEngine((result as { source?: string }).source || 'YOLO');
          }
        } else {
          votesRef.current = [];
          setOverlay(null);
        }
      } finally {
        busyRef.current = false;
        setBusy(false);
      }
    }, 850);
    return () => window.clearInterval(timer);
  }, [running, qwenBusy, onIdentify]);

  useEffect(() => () => stop(), []);

  const confirmWithQwen = async () => {
    if (!videoRef.current) return;
    setQwenBusy(true);
    setError('');
    try {
      const still = captureVideoFrame(videoRef.current, 1024);
      const result = await onIdentify(still, false);
      if (result && result.detectedProduct !== 'Unidentified Product') {
        setOverlay(result);
        setEngine((result as { source?: string }).source || 'Qwen-VL');
      } else {
        setError('Qwen did not see a clear appliance. Fill the frame and try again.');
      }
    } catch {
      setError('Qwen is offline. Start Ollama, then try again.');
    } finally {
      setQwenBusy(false);
    }
  };

  return (
    <div className="mb-6 overflow-hidden rounded-2xl border border-border bg-card">
      <div className="relative bg-black">
        <video ref={videoRef} playsInline muted className="h-[240px] w-full object-cover" />
        {overlay?.boundingBox?.length === 4 && (
          <div
            className="pointer-events-none absolute rounded border-2 border-accent bg-accent/15"
            style={{
              top: `${overlay.boundingBox[0] * 100}%`,
              left: `${overlay.boundingBox[1] * 100}%`,
              height: `${Math.max(10, (overlay.boundingBox[2] - overlay.boundingBox[0]) * 100)}%`,
              width: `${Math.max(10, (overlay.boundingBox[3] - overlay.boundingBox[1]) * 100)}%`,
            }}
          >
            <span className="absolute -top-5 left-0 rounded bg-accent px-1.5 py-0.5 text-[9px] font-bold text-accent-foreground">
              {overlay.detectedProduct} · {Math.round(overlay.confidence * 100)}% · {engine}
            </span>
          </div>
        )}
      </div>
      <div className="flex flex-col gap-3 p-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0 text-xs text-muted-foreground">
            {overlay
            ? `${overlay.detectedProduct} · ${engine}`
            : 'Live view is YOLO only (~150–400ms), not Qwen. It stays blank rather than guess a washing machine on an empty room. Confirm with Qwen needs qwen2.5vl:3b — qwen3-vl:8b times out on this PC.'}
          {error && <div className="text-red-600">{error}</div>}
        </div>
        <div className="flex shrink-0 gap-2">
          <button
            type="button"
            disabled={!running || qwenBusy}
            onClick={() => void confirmWithQwen()}
            className="inline-flex items-center gap-1.5 rounded-xl border border-border px-3 py-2 text-xs font-semibold disabled:opacity-40"
          >
            {qwenBusy ? <LoaderCircle size={14} className="animate-spin" /> : <Sparkles size={14} />}
            Confirm with Qwen
          </button>
          <button
            type="button"
            onClick={() => (running ? stop() : void start())}
            className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-3 py-2 text-xs font-semibold text-primary-foreground"
          >
            {busy ? <LoaderCircle size={14} className="animate-spin" /> : running ? <Square size={14} /> : <Camera size={14} />}
            {running ? 'Stop' : 'Start camera'}
          </button>
        </div>
      </div>
    </div>
  );
}
