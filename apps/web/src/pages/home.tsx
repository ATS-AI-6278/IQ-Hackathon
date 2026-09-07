import { useEffect, useRef, useState, type ReactNode } from 'react';
import { Link } from 'wouter';
import {
  ArrowRight,
  BadgeCheck,
  Bot,
  Box,
  CalendarClock,
  Camera,
  Cpu,
  FileText,
  Fingerprint,
  History,
  Home,
  Layers,
  Lock,
  MapPin,
  RefreshCw,
  ScanLine,
  Send,
  ShieldCheck,
  Sparkles,
  Wrench,
  type LucideIcon,
} from 'lucide-react';
import { SpatialTilt } from '@/components/spatial-ui';

function cx2(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ');
}

function Reveal({ children, delay = 0, className = '' }: { children: ReactNode; delay?: number; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setVisible(true);
            observer.disconnect();
            break;
          }
        }
      },
      { threshold: 0.16 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  return (
    <div
      ref={ref}
      style={{ transitionDelay: `${delay}ms` }}
      className={cx2('reveal', visible && 'is-visible', className)}
      data-testid="reveal-block"
    >
      {children}
    </div>
  );
}

function SectionTag({ children, center = false }: { children: ReactNode; center?: boolean }) {
  return (
    <div className={cx2('mb-5 flex items-center gap-3 font-mono-ui text-[10px] font-medium uppercase tracking-[.24em] text-muted-foreground', center && 'justify-center')}>
      <span className="h-2 w-2 rounded-full bg-accent/80 shadow-[0_0_12px_hsl(var(--accent)/.6)]" />
      {children}
    </div>
  );
}

/* ───────────────────────── Ask Hovira ───────────────────────── */

type AskReply = { title: string; body: string; sources: string[] };

function replyFor(raw: string): AskReply {
  const q = raw.toLowerCase();
  if (q.includes('attention')) {
    return {
      title: '3 things need your attention',
      body: 'Your AC warranty ends soon, the water purifier filter is nearing replacement, and the washing machine is due maintenance. Each one links back to its source record in your household memory.',
      sources: ['Household memory', 'Warranty radar', 'Service log'],
    };
  }
  if (q.includes('warranty')) {
    return {
      title: 'Where is my AC warranty?',
      body: 'Your AC passport DPP-00038 holds it — 5-year coverage from TechDeal Appliances, OCR-extracted from the original invoice. It expires in roughly 40 days.',
      sources: ['DPP-00038 · AC passport', 'INV-2024-7104 · OCR extract'],
    };
  }
  if (q.includes('servic')) {
    return {
      title: 'When was my washing machine serviced?',
      body: 'The Electrolux washer was last serviced in February — filter cleaned and drum checked. It is due again soon, so I flagged it in your insights.',
      sources: ['ELFW7637AW · service history', 'DPP-00040 · passport'],
    };
  }
  if (q.includes('changed')) {
    return {
      title: 'What changed recently in your home',
      body: 'This week: a Dyson passport was linked, the utility room was re-mapped, and two invoices were OCR-imported. Nothing unusual detected since.',
      sources: ['Household memory · history', 'Room map v4'],
    };
  }
  return {
    title: 'Rooted in your household memory',
    body: 'I combine passport records, scanned documents, room maps and service history to answer — all processed locally on your device.',
    sources: ['Household memory', 'Local processing'],
  };
}

const ASK_SUGGESTIONS = ['What needs my attention?', 'Where is my AC warranty?', 'When was my washing machine serviced?', 'What changed recently?'];

function AskSection() {
  const [value, setValue] = useState('');
  const [thinking, setThinking] = useState(false);
  const [reply, setReply] = useState<AskReply | null>(null);

  const runAsk = (prompt: string) => {
    setValue(prompt);
    setThinking(true);
    setReply(null);
    window.setTimeout(() => {
      setReply(replyFor(prompt));
      setThinking(false);
    }, 950);
  };

  const submit = () => {
    const prompt = value.trim();
    if (prompt) runAsk(prompt);
  };

  return (
    <section id="ask" className="mx-auto w-full max-w-[780px] scroll-mt-28" data-testid="section-ask">
      <Reveal>
        <SectionTag>Ask Hovira</SectionTag>
      </Reveal>
      <Reveal delay={80}>
        <div className="command-shell flex items-center gap-3 p-2 pl-5 md:gap-4 md:p-2.5 md:pl-6">
          <Bot size={18} className="shrink-0 text-accent/90" strokeWidth={2} />
          <input
            value={value}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') submit();
            }}
            placeholder="Ask anything about your home…"
            aria-label="Ask Hovira anything about your home"
            className="h-11 min-w-0 flex-1 md:h-11"
            data-testid="input-ask-hovira"
          />
          <button
            onClick={submit}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent text-primary shadow-[0_10px_26px_hsl(var(--accent)/.35)] transition-all duration-200 hover:-translate-y-0.5 hover:bg-accent/90"
            aria-label="Ask Hovira"
            data-testid="button-ask-hovira"
          >
            <Send size={16} strokeWidth={2.2} />
          </button>
        </div>
      </Reveal>
      <Reveal delay={150} className="mt-5 flex flex-wrap items-center justify-center gap-2">
        {ASK_SUGGESTIONS.map((suggestion, index) => (
          <button key={suggestion} onClick={() => runAsk(suggestion)} className="command-hint" data-testid={`ask-hint-${index}`}>
            <Sparkles size={11} className="text-accent/80" />
            {suggestion}
          </button>
        ))}
      </Reveal>
      {(thinking || reply) && (
        <Reveal className="mt-7">
          <div className="glass relative overflow-hidden rounded-[28px] border-white/12 p-6 md:p-8" data-testid="ask-result">
            <div className="glass-sheen pointer-events-none absolute inset-0" aria-hidden="true" />
            {thinking ? (
              <div className="flex items-center gap-3 text-[13px] text-muted-foreground">
                <span className="typing-dots flex items-center gap-1"><span /><span /><span /></span>
                Hovira is reading your home memory…
              </div>
            ) : (
              reply && (
                <div>
                  <div className="flex items-center gap-2.5">
                    <BadgeCheck size={18} className="shrink-0 text-accent" />
                    <h3 className="font-display text-lg font-semibold tracking-tight text-foreground">{reply.title}</h3>
                  </div>
                  <p className="mt-2.5 max-w-[58ch] text-sm leading-relaxed text-muted-foreground">{reply.body}</p>
                  <div className="mt-5 flex flex-wrap gap-2">
                    {reply.sources.map((source) => (
                      <span key={source} className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 font-mono-ui text-[10px] uppercase tracking-[.12em] text-muted-foreground/80">
                        {source}
                      </span>
                    ))}
                  </div>
                  <div className="mt-5 border-t border-white/10 pt-4 text-[11px] text-muted-foreground/60">
                    Demo: answers are simulated on-device to illustrate household intelligence.
                  </div>
                </div>
              )
            )}
          </div>
        </Reveal>
      )}
    </section>
  );
}

/* ─────────────────────── Household memory ─────────────────────── */

const MEMORY_LAYERS: Array<{ key: string; label: string; icon: LucideIcon; detail: string }> = [
  { key: 'products', label: 'Products', icon: Box, detail: '42 product records that turn every purchase into memory.' },
  { key: 'rooms', label: 'Rooms', icon: Home, detail: '4 spaces mapped from quiet camera passes.' },
  { key: 'documents', label: 'Documents', icon: FileText, detail: '56 invoices and warranty papers, OCR-extracted.' },
  { key: 'events', label: 'Events', icon: CalendarClock, detail: '3 service events lined up this month.' },
  { key: 'warranty', label: 'Warranty', icon: ShieldCheck, detail: '4 active coverages. Nearest due: 2026.' },
  { key: 'maintenance', label: 'Maintenance', icon: Wrench, detail: 'Purifier filter replacement due in 14 days.' },
  { key: 'history', label: 'History', icon: History, detail: '92 changes tracked this year — your home, remembered.' },
];

function MemorySystem() {
  const [active, setActive] = useState<(typeof MEMORY_LAYERS)[number] | null>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const [ring, setRing] = useState(150);

  useEffect(() => {
    const el = stageRef.current;
    if (!el) return;
    const update = () => {
      const width = el.getBoundingClientRect().width;
      if (width < 1) return;
      setRing(Math.max(94, Math.min(width / 2 - 72, 168)));
    };
    update();
    const observer = new ResizeObserver(update);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const count = MEMORY_LAYERS.length;

  return (
    <section id="memory" className="mx-auto w-full max-w-[900px] scroll-mt-28" data-testid="section-memory">
      <Reveal>
        <SectionTag center>Household memory</SectionTag>
        <h2 className="text-center font-display text-3xl font-semibold tracking-[-.04em] text-foreground md:text-5xl md:leading-[1.05]">
          One system. Every layer of your home.
        </h2>
      </Reveal>
      <Reveal delay={110}>
        <div ref={stageRef} className="memory-stage mx-auto mt-12 h-[340px] w-full max-w-[420px] md:h-[420px]" data-testid="memory-stage">
          <div className="memory-ring-faint" aria-hidden="true" />
          <div className="memory-ring-dashed" aria-hidden="true" />
          {MEMORY_LAYERS.map((layer, index) => {
            const angle = (index / count) * Math.PI * 2 - Math.PI / 2;
            const Icon = layer.icon;
            const isActive = active?.key === layer.key;
            return (
              <button
                key={layer.key}
                onClick={() => setActive(isActive ? null : layer)}
                className={cx2('node-chip', isActive && 'active')}
                style={{ left: `calc(50% + ${Math.cos(angle) * ring}px)`, top: `calc(50% + ${Math.sin(angle) * ring}px)` }}
                aria-pressed={isActive}
                aria-label={`Explore ${layer.label.toLowerCase()}`}
                data-testid={`memory-node-${layer.key}`}
              >
                <Icon size={16} strokeWidth={isActive ? 2.4 : 1.9} className="text-accent/90" />
                <span className="hidden md:inline">{layer.label}</span>
              </button>
            );
          })}
          <div className="home-orb absolute left-1/2 top-1/2 z-10 -translate-x-1/2 -translate-y-1/2" data-testid="memory-center">
            <Fingerprint size={18} className="text-accent" strokeWidth={2.2} />
            <span className="font-mono-ui text-[10px] font-semibold uppercase tracking-[.22em] text-foreground/80">Home</span>
          </div>
        </div>
      </Reveal>
      <Reveal delay={160}>
        <div className="relative mx-auto mt-8 flex min-h-[64px] w-full max-w-[560px] items-center justify-center gap-3 rounded-[22px] border border-white/10 bg-white/[0.04] px-5 py-4 text-center backdrop-blur-xl" data-testid="memory-readout">
          {active ? (
            <>
              <active.icon size={15} className="shrink-0 text-accent" />
              <span className="text-[13px] leading-snug text-foreground/80">
                <span className="font-semibold text-foreground">{active.label}</span>
                <span className="text-muted-foreground"> — {active.detail}</span>
              </span>
            </>
          ) : (
            <span className="text-[12px] text-muted-foreground">Tap a layer to read the household graph.</span>
          )}
        </div>
      </Reveal>
    </section>
  );
}

/* ───────────────────────── Hovira insight ───────────────────────── */

const INSIGHTS = [
  { icon: ShieldCheck, title: 'AC', text: 'Warranty ending soon', tag: 'Due in ~40 days' },
  { icon: Wrench, title: 'Water purifier', text: 'Filter replacement approaching', tag: '14 days left' },
  { icon: RefreshCw, title: 'Washing machine', text: 'Maintenance due', tag: 'Next week' },
];

function InsightSection() {
  const [showWhy, setShowWhy] = useState(false);
  const [showSources, setShowSources] = useState(false);

  return (
    <section id="insight" className="mx-auto w-full max-w-[900px] scroll-mt-28" data-testid="section-insight">
      <Reveal>
        <SectionTag center>Hovira insight</SectionTag>
        <h2 className="text-center font-display text-3xl font-semibold tracking-[-.04em] text-foreground md:text-5xl md:leading-[1.05]">
          I noticed 3 things that may need your attention.
        </h2>
      </Reveal>
      <Reveal delay={110}>
        <div className="glass relative mt-10 overflow-hidden rounded-[30px] border-white/12 p-6 md:p-8" data-testid="insight-card">
          <div className="glass-sheen pointer-events-none absolute inset-0" aria-hidden="true" />
          <div className="grid gap-3 md:grid-cols-3">
            {INSIGHTS.map((insight) => {
              const Icon = insight.icon;
              return (
                <div key={insight.title} className="relative rounded-[20px] border border-white/10 bg-white/[0.045] p-5 backdrop-blur-xl transition-transform duration-300 hover:-translate-y-1">
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-accent/25 bg-accent/10 text-accent">
                      <Icon size={17} strokeWidth={2} />
                    </div>
                    <span className="font-display text-[15px] font-semibold tracking-tight text-foreground">{insight.title}</span>
                  </div>
                  <p className="mt-3 text-[13px] leading-snug text-muted-foreground">{insight.text}</p>
                  <span className="mt-4 inline-flex rounded-full border border-accent/20 bg-accent/[0.07] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[.14em] text-accent/90">{insight.tag}</span>
                </div>
              );
            })}
          </div>
          <div className="mt-8 flex flex-wrap items-center gap-3 border-t border-white/10 pt-6">
            <button onClick={() => setShowWhy((value) => !value)} className={cx2('command-hint', showWhy && 'border-accent/40 bg-accent/10 text-accent')} data-testid="button-insight-why">
              Why?
            </button>
            <button onClick={() => setShowSources((value) => !value)} className={cx2('command-hint', showSources && 'border-accent/40 bg-accent/10 text-accent')} data-testid="button-insight-sources">
              Sources
            </button>
            <span className="ml-auto text-[11px] text-muted-foreground/60">Demo insight · simulated from passport, scan & memory data</span>
          </div>
          {(showWhy || showSources) && (
            <div className="page-enter mt-5 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-[13px] leading-relaxed text-muted-foreground" data-testid="insight-detail">
              {showWhy && (
                <p>
                  Hovira cross-checks warranty expiry (DPP-00038), consumable thresholds and the service calendar, then weights them by recency and criticality. The reasoning runs locally — nothing leaves your device.
                </p>
              )}
              {showSources && (
                <div className="flex flex-wrap gap-2">
                  {['Warranty record DPP-00038', 'OCR invoice INV-2024-7104', 'Service log · Electrolux', 'Room map v4'].map((source) => (
                    <span key={source} className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 font-mono-ui text-[10px] uppercase tracking-[.12em] text-muted-foreground/80">
                      {source}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </Reveal>
    </section>
  );
}

/* ───────────────────────── Passport showcase ───────────────────────── */

function PassportShowcase() {
  const specimen = {
    name: 'Electrolux EcoCare 800',
    brand: 'Electrolux',
    model: 'ELFW7637AW',
    serial: 'EL-800-44910',
    warranty: '5 years · inverter motor',
    location: 'Utility room',
    documents: ['Warranty certificate', 'Original invoice INV-HD-1092'],
    service: ['Apr · Filter cleaned', 'Feb · Drum service', 'Dec · Seal check'],
  };

  return (
    <section id="passport" className="mx-auto w-full max-w-[900px] scroll-mt-28" data-testid="section-passport">
      <Reveal>
        <SectionTag center>One product passport</SectionTag>
        <h2 className="text-center font-display text-3xl font-semibold tracking-[-.04em] text-foreground md:text-5xl md:leading-[1.05]">
          A product, fully remembered.
        </h2>
      </Reveal>
      <Reveal delay={110}>
        <SpatialTilt className="mt-10 rounded-[30px]">
          <div className="passport-grid-line relative overflow-hidden rounded-[30px] border border-white/12 bg-[rgba(18,19,23,.72)] p-6 backdrop-blur-2xl md:p-9" data-testid="passport-card">
            <div className="glass-sheen pointer-events-none absolute inset-0" aria-hidden="true" />
            <div className="relative flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-accent/15 text-accent">
                  <Fingerprint size={19} strokeWidth={2.1} />
                </div>
                <div>
                  <div className="font-mono-ui text-[9px] font-medium uppercase tracking-[.22em] text-muted-foreground">Digital product passport</div>
                  <div className="font-display text-[15px] font-semibold tracking-tight text-foreground">{specimen.name}</div>
                </div>
              </div>
              <span className="inline-flex items-center gap-1.5 rounded-full border border-teal-400/25 bg-teal-400/10 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[.14em] text-teal-300">
                <BadgeCheck size={12} /> Verified · YOLO sync
              </span>
            </div>

            <div className="relative mt-8 grid gap-8 md:grid-cols-[1.15fr_1fr]">
              <div className="space-y-3">
                {[
                  ['Brand', specimen.brand],
                  ['Model', specimen.model],
                  ['Serial', specimen.serial],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-baseline justify-between gap-4 border-b border-white/[0.07] pb-2.5">
                    <span className="font-mono-ui text-[10px] uppercase tracking-[.18em] text-muted-foreground">{label}</span>
                    <span className="text-right font-mono-ui text-[12px] text-foreground/85">{value}</span>
                  </div>
                ))}
                <div className="flex flex-wrap gap-2 pt-1">
                  <span className="inline-flex items-center gap-1.5 rounded-full border border-accent/25 bg-accent/10 px-3 py-1.5 text-[11px] font-medium text-accent">
                    <ShieldCheck size={12} /> {specimen.warranty}
                  </span>
                  <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-[11px] font-medium text-foreground/75">
                    <MapPin size={12} /> {specimen.location}
                  </span>
                </div>
              </div>
              <div className="space-y-6">
                <div>
                  <div className="mb-2.5 font-mono-ui text-[9px] font-medium uppercase tracking-[.2em] text-muted-foreground">Documents</div>
                  <div className="flex flex-col gap-1.5">
                    {specimen.documents.map((doc) => (
                      <span key={doc} className="rounded-xl border border-white/[0.08] bg-white/[0.04] px-3.5 py-2.5 text-[12px] text-foreground/80">
                        <FileText size={12} className="mr-2 inline -translate-y-px text-accent/80" />
                        {doc}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="mb-2.5 font-mono-ui text-[9px] font-medium uppercase tracking-[.2em] text-muted-foreground">Service history</div>
                  <div className="flex flex-col gap-1.5">
                    {specimen.service.map((entry) => (
                      <span key={entry} className="rounded-xl border border-white/[0.08] bg-white/[0.04] px-3.5 py-2.5 text-[12px] text-foreground/80">
                        <Wrench size={12} className="mr-2 inline -translate-y-px text-accent/80" />
                        {entry}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="relative mt-8 flex justify-end border-t border-white/10 pt-5">
              <Link href="/passports" className="inline-flex items-center gap-1.5 text-[13px] font-medium text-accent transition-colors hover:text-white" data-testid="link-open-library">
                Open the full library <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </SpatialTilt>
      </Reveal>
    </section>
  );
}

/* ───────────────────────── Local intelligence ───────────────────────── */

const LOCAL_PILLARS = [
  { icon: Camera, label: 'Qwen Vision', text: 'on-device camera understanding, object & document detection' },
  { icon: Layers, label: 'Household Memory', text: 'a living graph of everything your home contains' },
  { icon: Cpu, label: 'Local Processing', text: 'no cloud account, no upload, no latency' },
  { icon: Lock, label: 'Private by Design', text: 'the memory stays with you, on your hardware' },
];

function LocalIntelligence() {
  return (
    <section id="local" className="mx-auto w-full max-w-[900px] scroll-mt-28" data-testid="section-local">
      <Reveal>
        <SectionTag center>Local intelligence</SectionTag>
      </Reveal>
      <Reveal delay={90}>
        <div className="mt-2 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {LOCAL_PILLARS.map((pillar) => {
            const Icon = pillar.icon;
            return (
              <div key={pillar.label} className="relative rounded-[22px] border border-white/10 bg-white/[0.045] p-5 text-center backdrop-blur-xl transition-transform duration-300 hover:-translate-y-1" data-testid={`local-pillar-${pillar.label.toLowerCase().replaceAll(' ', '-')}`}>
                <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.06] text-accent">
                  <Icon size={19} strokeWidth={1.9} />
                </div>
                <div className="mt-3.5 font-display text-[14px] font-semibold tracking-tight text-foreground">{pillar.label}</div>
                <p className="mt-1.5 text-[11.5px] leading-snug text-muted-foreground">{pillar.text}</p>
              </div>
            );
          })}
        </div>
        <p className="mt-5 text-center text-[11px] text-muted-foreground/60">
          Demo: simulated in the browser. Vision, OCR and scanning are genuine on the local compute backend.
        </p>
      </Reveal>
    </section>
  );
}

/* ───────────────────────── Finale ───────────────────────── */

const FINALE_WORDS = ['Products', 'Documents', 'Rooms', 'Events', 'Vision', 'Memory', 'AI'];

function FutureVision() {
  return (
    <section id="future" className="mx-auto w-full max-w-[1100px] px-2" data-testid="section-future">
      <Reveal className="text-center">
        <SectionTag center>From product passport to household intelligence</SectionTag>
      </Reveal>
      <Reveal delay={80} className="mt-8 flex flex-wrap items-center justify-center gap-2">
        {FINALE_WORDS.map((word, index) => (
          <span key={word} className="command-hint" style={{ transitionDelay: `${index * 40}ms` }}>
            {word}
          </span>
        ))}
      </Reveal>
      <Reveal delay={140} className="mt-12 text-center">
        <div className="finale-hovira text-aura-gradient" data-testid="text-finale-hovira">HOVIRA</div>
        <p className="mt-5 text-[13px] uppercase tracking-[.3em] text-muted-foreground">Private AI household intelligence</p>
      </Reveal>
      <Reveal delay={220} className="mt-10 flex flex-wrap items-center justify-center gap-3">
        <Link href="/passports" className="inline-flex items-center gap-2 rounded-full bg-accent px-6 py-3 text-sm font-semibold text-primary shadow-[0_14px_34px_hsl(var(--accent)/.28)] transition-all duration-200 hover:-translate-y-0.5 hover:bg-accent/90" data-testid="cta-library">
          Explore the passport library <ArrowRight size={15} />
        </Link>
        <Link href="/scan" className="inline-flex items-center gap-2 rounded-full border border-white/12 bg-white/[0.05] px-6 py-3 text-sm font-semibold text-foreground backdrop-blur-xl transition-all duration-200 hover:-translate-y-0.5 hover:border-accent/50 hover:bg-white/[0.08]" data-testid="cta-scan">
          <ScanLine size={15} /> Scan with live vision
        </Link>
      </Reveal>
      <Reveal delay={300} className="mt-8 text-center">
        <p className="text-[11px] leading-relaxed text-muted-foreground/55">
          Interactive demo — simulated intelligence, real design. Local processing, private by design.
        </p>
      </Reveal>
    </section>
  );
}

/* ───────────────────────── Page ───────────────────────── */

export function HomeShowcase() {
  return (
    <div className="mx-auto w-full max-w-[1180px]" data-testid="page-home">
      <section className="relative pt-8 text-center md:pb-6 md:pt-16" data-testid="section-hero">
        <Reveal>
          <div className="hero-badge">
            <span className="ai-live-dot shrink-0" />
            Private AI household intelligence
          </div>
        </Reveal>
        <Reveal delay={90}>
          <h1 className="display-title text-aura-gradient mx-auto mt-7 max-w-[16ch]">
            Your household, understood.
          </h1>
        </Reveal>
        <Reveal delay={180}>
          <p className="display-sub mx-auto mt-7">
            Hovira remembers the products, documents, spaces and history that make up your home.
          </p>
        </Reveal>
      </section>

      <div className="mt-16 space-y-24 md:mt-24 md:space-y-44">
        <AskSection />
        <MemorySystem />
        <InsightSection />
        <PassportShowcase />
        <LocalIntelligence />
        <FutureVision />
      </div>
    </div>
  );
}