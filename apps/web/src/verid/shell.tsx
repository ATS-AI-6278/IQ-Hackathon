import { type ReactNode, useEffect, useState } from 'react';
import { Link, useLocation } from 'wouter';
import { Camera, Fingerprint, Home, MessageCircle, Plus, Shield } from 'lucide-react';

const tabs = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/memory', label: 'Memory', icon: Fingerprint },
  { href: '/camera', label: 'Camera', icon: Camera },
  { href: '/ask', label: 'Ask', icon: MessageCircle },
];

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ');
}

export function VeridShell({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  const hideChrome = location.startsWith('/remember') && false;

  return (
    <div className="verid-app min-h-[100dvh] bg-background text-foreground">
      <header className="sticky top-0 z-20 border-b border-border/80 bg-background/90 px-5 py-4 backdrop-blur-md md:px-10">
        <div className="mx-auto flex max-w-[920px] items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5" data-testid="link-verid-home">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <Fingerprint size={16} />
            </span>
            <span className="font-display text-[17px] font-semibold tracking-tight">Verid</span>
          </Link>
          <div className="flex items-center gap-2">
            <Link
              href="/privacy"
              className="hidden items-center gap-1.5 rounded-full px-3 py-1.5 text-[12px] text-muted-foreground hover:text-foreground sm:inline-flex"
            >
              <Shield size={13} /> Privacy
            </Link>
            <Link
              href="/remember"
              className="inline-flex items-center gap-1.5 rounded-full bg-primary px-3.5 py-2 text-[12px] font-semibold text-primary-foreground"
              data-testid="link-remember"
            >
              <Plus size={14} /> Remember
            </Link>
          </div>
        </div>
      </header>

      <main className={cx('mx-auto max-w-[920px] px-5 pb-28 pt-8 md:px-10 md:pt-12', hideChrome && 'pb-10')}>
        {children}
      </main>

      <nav
        className="fixed inset-x-0 bottom-0 z-30 border-t border-border/80 bg-background/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-md"
        aria-label="Verid"
      >
        <div className="mx-auto grid max-w-[920px] grid-cols-4 px-2 py-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const active = tab.href === '/' ? location === '/' : location.startsWith(tab.href);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cx(
                  'flex flex-col items-center gap-1 rounded-xl py-2 text-[11px] font-medium',
                  active ? 'text-foreground' : 'text-muted-foreground',
                )}
                data-testid={`tab-${tab.label.toLowerCase()}`}
              >
                <Icon size={20} strokeWidth={active ? 2.3 : 1.7} />
                {tab.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}

export function QuietLine({ children }: { children: ReactNode }) {
  return <p className="max-w-[42ch] text-[15px] leading-relaxed text-muted-foreground">{children}</p>;
}

export function useAsync<T>(loader: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let live = true;
    setLoading(true);
    loader()
      .then((value) => {
        if (live) {
          setData(value);
          setError(false);
        }
      })
      .catch(() => {
        if (live) setError(true);
      })
      .finally(() => {
        if (live) setLoading(false);
      });
    return () => {
      live = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return { data, error, loading, reload: () => loader().then(setData) };
}
