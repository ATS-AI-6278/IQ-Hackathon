import { useEffect, useState } from 'react';
import QRCode from 'qrcode';
import { Smartphone, X, ExternalLink, QrCode, Sparkles, Check } from 'lucide-react';
import { fetchLan } from '@/lib/household';

interface PhoneConnectModalProps {
  isOpen: boolean;
  onClose: () => void;
      targetPath?: string;
}

export function PhoneConnectModal({ isOpen, onClose, targetPath = '/camera' }: PhoneConnectModalProps) {
  const [qrUrl, setQrUrl] = useState<string>('');
  const [mobileUrl, setMobileUrl] = useState<string>('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    const apply = (url: string) => {
      if (cancelled) return;
      setMobileUrl(url);
      QRCode.toDataURL(url, {
        width: 260,
        margin: 2,
        color: { dark: '#0f172a', light: '#ffffff' },
      })
        .then(setQrUrl)
        .catch(console.error);
    };

    const localHost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (!localHost) {
      apply(`${window.location.origin}${targetPath}`);
      return () => {
        cancelled = true;
      };
    }

    void fetchLan().then((lan) => {
      const origin = (lan.urls[0] || lan.preferred || window.location.origin).replace(/\/(camera|scan)$/i, '');
      apply(`${origin}${targetPath}`);
    });

    return () => {
      cancelled = true;
    };
  }, [isOpen, targetPath]);

  if (!isOpen) return null;

  const copyUrl = () => {
    navigator.clipboard?.writeText(mobileUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-primary/40 p-4 backdrop-blur-md">
      <div className="relative w-full max-w-md rounded-3xl border border-border bg-card p-6 shadow-2xl md:p-8">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-xl p-2 text-muted-foreground transition hover:bg-secondary hover:text-foreground"
          aria-label="Close modal"
        >
          <X size={18} />
        </button>

        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent/20 text-accent">
            <Smartphone size={22} />
          </div>
          <div>
            <div className="font-mono-ui text-[10px] font-semibold uppercase tracking-[.18em] text-accent">
              iQOO Hackathon · Creative Phone Feature
            </div>
            <h3 className="font-display text-xl font-bold text-foreground">Scan with Your Phone</h3>
          </div>
        </div>

        <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
          Point your smartphone camera at the QR code below to launch the live mobile camera scanner directly on your phone.
        </p>

        <div className="mt-5 flex flex-col items-center justify-center rounded-2xl border border-border bg-white p-5 shadow-inner">
          {qrUrl ? (
            <img src={qrUrl} alt="Mobile Scanner QR Code" className="h-52 w-52 rounded-xl object-contain shadow-sm" />
          ) : (
            <div className="flex h-52 w-52 items-center justify-center text-muted-foreground">
              <QrCode size={40} className="animate-spin" />
            </div>
          )}
          <span className="mt-3 flex items-center gap-1.5 font-mono-ui text-[10px] font-medium text-slate-600">
            <Sparkles size={12} className="text-teal-600" /> Direct mobile camera bridge
          </span>
        </div>

        <div className="mt-4 rounded-xl border border-border bg-secondary/50 p-3">
          <div className="flex items-center justify-between text-xs">
            <span className="truncate font-mono-ui text-[11px] text-muted-foreground">{mobileUrl}</span>
            <button
              onClick={copyUrl}
              className="ml-2 flex items-center gap-1 text-[11px] font-semibold text-accent hover:underline"
            >
              {copied ? <Check size={12} className="text-teal-600" /> : <ExternalLink size={12} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          </div>
        </div>

        <div className="mt-5 text-center">
          <button
            onClick={onClose}
            className="w-full rounded-xl bg-primary py-2.5 text-xs font-semibold text-primary-foreground shadow transition hover:bg-primary/90"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
