import { type ButtonHTMLAttributes, type ReactNode, useMemo, useRef, useState } from 'react';
import { QueryClient, QueryClientProvider, useQueryClient } from '@tanstack/react-query';
import {
  Activity as ActivityIcon,
  ArrowLeft,
  ArrowRight,
  BadgeCheck,
  Box,
  Camera,
  Check,
  ChevronDown,
  CircleAlert,
  Clock3,
  CloudUpload,
  Copy,
  FileCheck2,
  FileText,
  Fingerprint,
  FolderOpen,
  Gauge,
  Image as ImageIcon,
  Link2,
  LoaderCircle,
  Menu,
  PackageCheck,
  Pencil,
  Plus,
  RefreshCw,
  Search,
  ScanLine,
  Settings2,
  ShieldCheck,
  Sparkles,
  Tag,
  X,
} from 'lucide-react';
import {
  type Passport,
  type PassportInput,
  type PassportUpdate,
  type DocumentAnalysis,
  type ProductIdentification,
  type ProductMatchResponse,
  type ProductMatch,
  type DetectedProduct,
  type Activity,
  useAnalyzeDocument,
  useCreatePassport,
  useGetDashboardSummary,
  useGetPassport,
  useGetSystemStatus,
  useIdentifyProduct,
  useLinkProduct,
  useListActivity,
  useListPassports,
  useMatchProduct,
  useUpdatePassport,
  getGetDashboardSummaryQueryKey,
  getGetPassportQueryKey,
  getListActivityQueryKey,
  getListPassportsQueryKey,
} from '@workspace/api-client-react';
import { ErrorBoundary } from '@/components/error-boundary';
import NotFound from '@/pages/not-found';
import { Link, Route, Switch, useLocation, useParams, Router as WouterRouter } from 'wouter';
import { DEMO_PRESETS } from './demo-presets';

const queryClient = new QueryClient();

const navItems = [
  { href: '/', label: 'Overview', icon: Gauge },
  { href: '/passports', label: 'Passport library', icon: FolderOpen },
  { href: '/create', label: 'Create passport', icon: Plus },
  { href: '/scan', label: 'Scan product', icon: ScanLine },
  { href: '/activity', label: 'Activity', icon: ActivityIcon },
];

function formatDate(value?: string | null, withTime = false) {
  if (!value) return 'Not recorded';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('en-US', withTime ? { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' } : { month: 'short', day: 'numeric', year: 'numeric' }).format(date);
}

function money(value?: number | null, currency?: string | null) {
  if (value === null || value === undefined) return 'Not recorded';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: currency || 'USD' }).format(value);
}

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ');
}

function LogoMark() {
  return (
    <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-[11px] bg-accent text-primary shadow-[0_8px_18px_hsl(var(--accent)/.22)]" data-testid="brand-mark">
      <Fingerprint size={19} strokeWidth={2.5} />
      <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full border-2 border-sidebar bg-accent" />
    </div>
  );
}

function StatusPill({ status, label }: { status: string; label?: string }) {
  const normalized = status.toLowerCase();
  const good = ['verified', 'connected', 'high', 'linked'].includes(normalized);
  const pending = ['pending', 'medium', 'degraded'].includes(normalized);
  return (
    <span className={cx('inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[.11em]', good ? 'border-teal-200 bg-teal-50 text-teal-700' : pending ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-red-200 bg-red-50 text-red-700')} data-testid={`status-${normalized}`}>
      <span className={cx('h-1.5 w-1.5 rounded-full', good ? 'bg-teal-500' : pending ? 'bg-amber-500' : 'bg-red-500')} />
      {label || status}
    </span>
  );
}

function Button({ children, variant = 'primary', className, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'ghost' | 'danger' }) {
  return (
    <button
      className={cx(
        'inline-flex min-h-10 items-center justify-center gap-2 rounded-xl px-4 text-sm font-semibold transition-all duration-200 focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-not-allowed disabled:opacity-50',
        variant === 'primary' && 'bg-primary text-primary-foreground shadow-[0_8px_20px_hsl(var(--primary)/.14)] hover:-translate-y-0.5 hover:bg-primary/90',
        variant === 'secondary' && 'border border-border bg-card text-foreground hover:-translate-y-0.5 hover:border-primary/30 hover:bg-secondary',
        variant === 'ghost' && 'text-muted-foreground hover:bg-muted hover:text-foreground',
        variant === 'danger' && 'border border-red-200 bg-red-50 text-red-700 hover:bg-red-100',
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}

function Shell({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const pageLabel = navItems.find((item) => item.href === location)?.label || (location.startsWith('/passports/') ? 'Passport detail' : 'Workspace');
  return (
    <div className="app-grain min-h-[100dvh] bg-background text-foreground">
      <aside className={cx('fixed inset-y-0 left-0 z-30 flex w-[252px] flex-col bg-sidebar px-4 py-5 text-sidebar-foreground transition-transform duration-300 md:translate-x-0', mobileOpen ? 'translate-x-0' : '-translate-x-full')}>
        <div className="flex items-center gap-3 px-2">
          <LogoMark />
          <div>
            <div className="font-display text-[17px] font-semibold tracking-tight text-sidebar-foreground">Verid</div>
            <div className="font-mono-ui text-[9px] uppercase tracking-[.24em] text-sidebar-foreground/45">Product identity</div>
          </div>
          <button className="ml-auto rounded-lg p-1.5 text-sidebar-foreground/60 hover:bg-sidebar-accent md:hidden" onClick={() => setMobileOpen(false)} aria-label="Close navigation" data-testid="button-close-navigation"><X size={18} /></button>
        </div>
        <div className="mt-10 px-2 font-mono-ui text-[9px] uppercase tracking-[.2em] text-sidebar-foreground/40">Workspace</div>
        <nav className="mt-3 flex flex-1 flex-col gap-1" aria-label="Main navigation">
          {navItems.map((item) => {
            const active = item.href === '/' ? location === '/' : location.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link key={item.href} href={item.href} onClick={() => setMobileOpen(false)} className={cx('group flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium transition-colors', active ? 'bg-sidebar-accent text-sidebar-foreground' : 'text-sidebar-foreground/58 hover:bg-sidebar-accent/70 hover:text-sidebar-foreground')} data-testid={`link-nav-${item.label.toLowerCase().replaceAll(' ', '-')}`}>
                <Icon size={17} strokeWidth={active ? 2.3 : 1.8} className={cx(active && 'text-accent')} />
                <span>{item.label}</span>
                {active && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-accent" />}
              </Link>
            );
          })}
        </nav>
        <div className="rounded-2xl border border-sidebar-border bg-sidebar-accent/65 p-3.5">
          <div className="flex items-center gap-2 text-[11px] font-semibold text-sidebar-foreground"><ShieldCheck size={15} className="text-accent" /> Trust center</div>
          <p className="mt-2 text-[11px] leading-relaxed text-sidebar-foreground/52">Your records stay tied to their source evidence.</p>
          <Link href="/settings" className="mt-3 inline-flex items-center gap-1 text-[11px] font-semibold text-accent hover:underline" data-testid="link-trust-center">View service status <ArrowRight size={12} /></Link>
        </div>
        <div className="mt-5 flex items-center gap-3 border-t border-sidebar-border pt-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/20 font-display text-xs font-semibold text-accent" data-testid="avatar-account">AM</div>
          <div className="min-w-0"><div className="truncate text-xs font-semibold">Alex Morgan</div><div className="truncate text-[10px] text-sidebar-foreground/45">Operations team</div></div>
          <Link href="/settings" className="ml-auto text-sidebar-foreground/45 hover:text-accent" aria-label="Open settings" data-testid="link-account-settings"><Settings2 size={16} /></Link>
        </div>
      </aside>
      {mobileOpen && <button className="fixed inset-0 z-20 bg-primary/20 backdrop-blur-sm md:hidden" onClick={() => setMobileOpen(false)} aria-label="Close menu overlay" data-testid="button-menu-overlay" />}
      <main className="min-h-[100dvh] md:pl-[252px]">
        <header className="sticky top-0 z-10 flex h-[70px] items-center justify-between border-b border-border/70 bg-background/90 px-5 backdrop-blur-xl md:px-10">
          <div className="flex items-center gap-3">
            <button className="rounded-xl border border-border bg-card p-2 md:hidden" onClick={() => setMobileOpen(true)} aria-label="Open navigation" data-testid="button-open-navigation"><Menu size={19} /></button>
            <div className="font-mono-ui text-[10px] uppercase tracking-[.18em] text-muted-foreground">{pageLabel}</div>
          </div>
          <div className="flex items-center gap-2.5">
            <Link href="/scan" className="hidden items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-xs font-semibold transition hover:border-accent/70 hover:bg-accent/20 sm:inline-flex" data-testid="link-header-scan"><ScanLine size={15} /> Scan a product</Link>
            <Link href="/create" className="inline-flex items-center gap-2 rounded-xl bg-accent px-3.5 py-2 text-xs font-bold text-primary transition hover:-translate-y-0.5 hover:bg-accent/85" data-testid="link-header-create"><Plus size={15} /> <span className="hidden sm:inline">New passport</span></Link>
          </div>
        </header>
        <div className="page-enter px-5 py-7 md:px-10 md:py-10">{children}</div>
      </main>
    </div>
  );
}

function PageIntro({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: ReactNode }) {
  return (
    <div className="mb-8 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
      <div>
        <div className="mb-3 flex items-center gap-2 font-mono-ui text-[10px] font-medium uppercase tracking-[.2em] text-muted-foreground"><span className="h-1.5 w-1.5 rounded-full bg-accent" />{eyebrow}</div>
        <h1 className="font-display text-3xl font-semibold tracking-[-.04em] text-foreground md:text-[42px] md:leading-[1.04]" data-testid={`text-page-title-${eyebrow.toLowerCase().replaceAll(' ', '-')}`}>{title}</h1>
        <p className="mt-3 max-w-[650px] text-sm leading-relaxed text-muted-foreground md:text-[15px]">{description}</p>
      </div>
      {action}
    </div>
  );
}

function LoadingBlock({ rows = 3 }: { rows?: number }) {
  return <div className="space-y-3" data-testid="loading-state">{Array.from({ length: rows }).map((_, index) => <div key={index} className="skeleton h-[70px] rounded-2xl" />)}</div>;
}

function ErrorState({ onRetry, label = 'The record could not be loaded.' }: { onRetry?: () => void; label?: string }) {
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50/70 p-8 text-center" data-testid="error-state">
      <CircleAlert className="mx-auto text-red-600" size={24} />
      <h3 className="mt-3 text-sm font-semibold text-red-900">Something needs another look</h3>
      <p className="mt-1 text-xs text-red-700/80">{label}</p>
      {onRetry && <Button variant="secondary" className="mt-4 border-red-200 bg-transparent text-red-700" onClick={onRetry} data-testid="button-retry"><RefreshCw size={14} /> Try again</Button>}
    </div>
  );
}

function EmptyState({ icon: Icon = FolderOpen, title, description, action }: { icon?: typeof FolderOpen; title: string; description: string; action?: ReactNode }) {
  return (
    <div className="rounded-2xl border border-dashed border-border bg-card/60 p-12 text-center" data-testid="empty-state">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-secondary text-primary"><Icon size={22} /></div>
      <h3 className="mt-4 font-display text-lg font-semibold">{title}</h3>
      <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-muted-foreground">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

function Dashboard() {
  const summary = useGetDashboardSummary({ query: { queryKey: getGetDashboardSummaryQueryKey() } });
  const activity = useListActivity({ query: { queryKey: getListActivityQueryKey() } });
  const passports = useListPassports({}, { query: { queryKey: getListPassportsQueryKey({}) } });
  const stats = [
    { label: 'Total passports', value: summary.data?.totalPassports, icon: Fingerprint, detail: 'Identity records' },
    { label: 'Products scanned', value: summary.data?.productsScanned, icon: ScanLine, detail: 'Physical checks' },
    { label: 'Documents processed', value: summary.data?.documentsProcessed, icon: FileCheck2, detail: 'Source evidence' },
    { label: 'Successfully linked', value: summary.data?.successfullyLinked, icon: Link2, detail: 'Verified matches' },
  ];
  return (
    <div className="mx-auto max-w-[1360px]">
      <PageIntro eyebrow="Workspace overview" title="Identity, made legible." description="A calm home for every product record — from the first invoice to the final physical match." action={<Link href="/create" className="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-primary px-4 text-sm font-semibold text-primary-foreground shadow-[0_8px_20px_hsl(var(--primary)/.14)] transition hover:-translate-y-0.5 hover:bg-primary/90" data-testid="link-create-dashboard"><Plus size={16} /> Create passport</Link>} />
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4" aria-label="Workspace metrics">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return <div className={cx('rise-in rounded-2xl border border-border bg-card p-5 shadow-[0_8px_24px_hsl(var(--primary)/.025)]', `delay-${index + 1}`)} key={stat.label} data-testid={`card-metric-${stat.label.toLowerCase().replaceAll(' ', '-')}`}>
            <div className="flex items-start justify-between"><div className="flex h-9 w-9 items-center justify-center rounded-xl bg-secondary text-primary"><Icon size={17} /></div><span className="font-mono-ui text-[10px] text-muted-foreground">LIVE</span></div>
            <div className="mt-5 font-display text-[32px] font-semibold tracking-[-.04em]">{summary.isLoading ? <span className="inline-block h-9 w-14 skeleton rounded-lg" /> : stat.value ?? 0}</div>
            <div className="mt-1 text-sm font-semibold">{stat.label}</div><div className="mt-1 text-xs text-muted-foreground">{stat.detail}</div>
          </div>;
        })}
      </section>
      <div className="mt-8 grid gap-6 xl:grid-cols-[1.2fr_.8fr]">
        <section className="overflow-hidden rounded-2xl border border-border bg-card">
          <div className="flex items-center justify-between border-b border-border px-5 py-4"><div><h2 className="font-display text-lg font-semibold">Recent passports</h2><p className="mt-0.5 text-xs text-muted-foreground">The latest identities entering your workspace.</p></div><Link href="/passports" className="inline-flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary/70" data-testid="link-view-all-passports">View library <ArrowRight size={13} /></Link></div>
          {passports.isLoading ? <div className="p-5"><LoadingBlock rows={4} /></div> : passports.isError ? <div className="p-5"><ErrorState onRetry={() => passports.refetch()} /></div> : passports.data?.length ? <div className="divide-y divide-border">{passports.data.slice(0, 5).map((passport) => <PassportRow passport={passport} key={passport.passportId} />)}</div> : <div className="p-5"><EmptyState icon={Fingerprint} title="No identities yet" description="Start with an invoice, receipt, or product document." action={<Link href="/create" className="inline-flex items-center gap-2 rounded-xl bg-primary px-3.5 py-2.5 text-xs font-semibold text-primary-foreground" data-testid="link-empty-create"><Plus size={14} /> Create first passport</Link>} /></div>}
        </section>
        <section className="rounded-2xl border border-border bg-primary p-5 text-primary-foreground">
          <div className="flex items-center justify-between"><div><h2 className="font-display text-lg font-semibold">Activity pulse</h2><p className="mt-0.5 text-xs text-primary-foreground/55">What changed recently.</p></div><ActivityIcon size={18} className="text-accent" /></div>
          {activity.isLoading ? <div className="mt-6 space-y-4">{[1, 2, 3].map((item) => <div className="skeleton h-12 rounded-xl bg-primary-foreground/10" key={item} />)}</div> : activity.data?.length ? <div className="mt-6 space-y-5">{activity.data.slice(0, 5).map((item) => <ActivityItem key={item.id} item={item} dark />)}</div> : <p className="mt-8 text-sm text-primary-foreground/60">No activity recorded yet.</p>}
          <Link href="/activity" className="mt-7 inline-flex items-center gap-1 text-xs font-semibold text-accent hover:underline" data-testid="link-view-activity">Open activity log <ArrowRight size={13} /></Link>
        </section>
      </div>
    </div>
  );
}

function PassportRow({ passport }: { passport: Passport }) {
  return <Link href={`/passports/${passport.passportId}`} className="group flex items-center gap-4 px-5 py-4 transition hover:bg-secondary/45" data-testid={`row-passport-${passport.passportId}`}>
    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-border bg-secondary text-primary"><Box size={18} /></div>
    <div className="min-w-0 flex-1"><div className="truncate text-sm font-semibold group-hover:text-primary">{passport.product}</div><div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground"><span>{passport.brand}</span><span className="h-1 w-1 rounded-full bg-border" /><span className="font-mono-ui">{passport.passportId}</span></div></div>
    <div className="hidden text-right sm:block"><StatusPill status={passport.verificationStatus} /><div className="mt-1 text-[10px] text-muted-foreground">{formatDate(passport.updatedAt)}</div></div><ArrowRight size={16} className="text-muted-foreground transition group-hover:translate-x-1 group-hover:text-primary" />
  </Link>;
}

function Passports() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const params = useMemo(() => ({ search: search || undefined, category: category || undefined, status: status || undefined }), [search, category, status]);
  const query = useListPassports(params, { query: { queryKey: getListPassportsQueryKey(params) } });
  return <div className="mx-auto max-w-[1360px]">
    <PageIntro eyebrow="Passport library" title="Your product registry." description="Search every identity record, inspect its evidence, and keep the chain of trust current." action={<Link href="/create" className="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-primary px-4 text-sm font-semibold text-primary-foreground" data-testid="link-create-library"><Plus size={16} /> New passport</Link>} />
    <div className="mb-5 flex flex-col gap-3 rounded-2xl border border-border bg-card p-3 md:flex-row">
      <label className="relative flex min-h-10 flex-1 items-center"><Search size={16} className="absolute left-3 text-muted-foreground" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search product, brand, serial, or passport ID" className="h-10 w-full rounded-xl border-0 bg-secondary pl-10 pr-3 text-sm outline-none ring-accent placeholder:text-muted-foreground focus:ring-2" data-testid="input-search-passports" /></label>
      <select value={category} onChange={(event) => setCategory(event.target.value)} className="h-10 rounded-xl border border-border bg-card px-3 text-sm text-foreground outline-none focus:ring-2 focus:ring-accent" data-testid="select-passport-category"><option value="">All categories</option><option value="Electronics">Electronics</option><option value="Furniture">Furniture</option><option value="Apparel">Apparel</option><option value="Appliance">Appliance</option></select>
      <select value={status} onChange={(event) => setStatus(event.target.value)} className="h-10 rounded-xl border border-border bg-card px-3 text-sm text-foreground outline-none focus:ring-2 focus:ring-accent" data-testid="select-passport-status"><option value="">Any status</option><option value="verified">Verified</option><option value="pending">Pending</option></select>
    </div>
    <div className="mb-4 flex items-center justify-between text-xs text-muted-foreground"><span data-testid="text-passport-count">{query.isLoading ? 'Loading registry…' : `${query.data?.length || 0} passport${query.data?.length === 1 ? '' : 's'}`}</span><span className="font-mono-ui uppercase tracking-[.14em]">Sorted by recent update</span></div>
    {query.isLoading ? <LoadingBlock rows={5} /> : query.isError ? <ErrorState onRetry={() => query.refetch()} /> : query.data?.length ? <div className="overflow-hidden rounded-2xl border border-border bg-card">{query.data.map((passport) => <PassportRow key={passport.passportId} passport={passport} />)}</div> : <EmptyState title="Nothing matches that search" description="Try a broader term, or add your first passport to begin the registry." icon={Search} action={<Button onClick={() => { setSearch(''); setCategory(''); setStatus(''); }} variant="secondary" data-testid="button-clear-passport-filters"><X size={14} /> Clear filters</Button>} />}
  </div>;
}

function DetailField({ label, value, mono = false }: { label: string; value?: string | number | null; mono?: boolean }) {
  return <div><div className="font-mono-ui text-[9px] uppercase tracking-[.16em] text-muted-foreground">{label}</div><div className={cx('mt-1.5 text-sm font-medium', mono && 'font-mono-ui text-xs')}>{value || 'Not recorded'}</div></div>;
}

function PassportDetail() {
  const { passportId = '' } = useParams<{ passportId: string }>();
  const query = useGetPassport(passportId, { query: { enabled: Boolean(passportId), queryKey: getGetPassportQueryKey(passportId) } });
  const update = useUpdatePassport();
  const client = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<PassportUpdate>({});
  const [saved, setSaved] = useState(false);
  const passport = query.data;
  const beginEdit = () => { if (!passport) return; setDraft({ product: passport.product, brand: passport.brand, model: passport.model, serialNumber: passport.serialNumber, category: passport.category, seller: passport.seller, warranty: passport.warranty, customerName: passport.customerName, orderId: passport.orderId, invoiceNumber: passport.invoiceNumber }); setEditing(true); };
  const save = () => update.mutate({ passportId, data: draft }, { onSuccess: (data) => { client.setQueryData(getGetPassportQueryKey(passportId), data); setEditing(false); setSaved(true); setTimeout(() => setSaved(false), 2200); } });
  if (query.isLoading) return <div className="mx-auto max-w-[1360px]"><LoadingBlock rows={4} /></div>;
  if (query.isError || !passport) return <div className="mx-auto max-w-[700px]"><ErrorState onRetry={() => query.refetch()} label="We could not find this passport." /></div>;
  return <div className="mx-auto max-w-[1200px]">
    <Link href="/passports" className="mb-7 inline-flex items-center gap-2 text-xs font-semibold text-muted-foreground hover:text-primary" data-testid="link-back-library"><ArrowLeft size={14} /> Back to passport library</Link>
    <div className="flex flex-col gap-5 border-b border-border pb-8 md:flex-row md:items-end md:justify-between">
      <div><div className="mb-3 flex items-center gap-2"><StatusPill status={passport.verificationStatus} /><span className="font-mono-ui text-[10px] text-muted-foreground">{passport.passportId}</span></div><h1 className="font-display text-4xl font-semibold tracking-[-.045em] md:text-5xl" data-testid="text-passport-product">{passport.product}</h1><p className="mt-2 text-sm text-muted-foreground">{passport.brand} · {passport.model} · {passport.category}</p></div>
      <div className="flex items-center gap-2"><Button variant="secondary" onClick={() => navigator.clipboard?.writeText(passport.passportId)} data-testid="button-copy-passport-id"><Copy size={14} /> Copy ID</Button><Button onClick={beginEdit} data-testid="button-edit-passport"><Pencil size={14} /> Edit record</Button></div>
    </div>
    {saved && <div className="mt-5 flex items-center gap-2 rounded-xl border border-teal-200 bg-teal-50 px-3 py-2 text-xs font-semibold text-teal-700" data-testid="status-passport-saved"><Check size={14} /> Passport updated</div>}
    <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_320px]">
      <section className="space-y-6">
        <div className="rounded-2xl border border-border bg-card p-5 md:p-7"><div className="mb-6 flex items-center justify-between"><div><h2 className="font-display text-xl font-semibold">Identity record</h2><p className="mt-1 text-xs text-muted-foreground">The core attributes of this product.</p></div><Fingerprint className="text-accent" size={24} /></div>
          {editing ? <EditFields draft={draft} setDraft={setDraft} onCancel={() => setEditing(false)} onSave={save} saving={update.isPending} /> : <div className="grid gap-x-8 gap-y-7 sm:grid-cols-2"><DetailField label="Product" value={passport.product} /><DetailField label="Brand" value={passport.brand} /><DetailField label="Model" value={passport.model} mono /><DetailField label="Serial number" value={passport.serialNumber} mono /><DetailField label="Category" value={passport.category} /><DetailField label="Document type" value={passport.documentType} /><DetailField label="Seller" value={passport.seller} /><DetailField label="Warranty" value={passport.warranty} /></div>}
        </div>
        <div className="rounded-2xl border border-border bg-card p-5 md:p-7"><div className="mb-6 flex items-center justify-between"><div><h2 className="font-display text-xl font-semibold">Purchase trail</h2><p className="mt-1 text-xs text-muted-foreground">Commercial details extracted from source evidence.</p></div><FileText className="text-accent" size={22} /></div><div className="grid gap-x-8 gap-y-7 sm:grid-cols-2"><DetailField label="Purchase date" value={formatDate(passport.purchaseDate)} /><DetailField label="Purchase price" value={money(passport.purchasePrice, passport.currency)} /><DetailField label="Customer" value={passport.customerName} /><DetailField label="Order ID" value={passport.orderId} mono /><DetailField label="Invoice number" value={passport.invoiceNumber} mono /><DetailField label="Source document" value={passport.sourceDocument} /></div></div>
      </section>
      <aside className="space-y-4">
        <div className="rounded-2xl border border-border bg-primary p-5 text-primary-foreground"><div className="flex items-center gap-2 text-xs font-semibold"><BadgeCheck size={17} className="text-accent" /> Verification posture</div><div className="mt-7 font-display text-4xl font-semibold">{passport.matchConfidence ? `${Math.round(passport.matchConfidence * 100)}%` : '—'}</div><p className="mt-1 text-xs text-primary-foreground/55">physical match confidence</p><div className="mt-5 h-1.5 overflow-hidden rounded-full bg-primary-foreground/15"><div className="h-full rounded-full bg-accent" style={{ width: `${Math.min(100, (passport.matchConfidence || 0) * 100)}%` }} /></div><p className="mt-5 text-xs leading-relaxed text-primary-foreground/65">Last updated {formatDate(passport.updatedAt, true)}. Your record is ready to be shared with confidence.</p></div>
        <div className="rounded-2xl border border-border bg-card p-5"><div className="flex items-center gap-2 text-xs font-semibold"><Clock3 size={15} className="text-accent" /> Record timeline</div><div className="mt-5 space-y-4 border-l border-border pl-4"><div><div className="text-xs font-semibold">Record created</div><div className="mt-1 text-[11px] text-muted-foreground">{formatDate(passport.createdAt, true)}</div></div><div><div className="text-xs font-semibold">Last reviewed</div><div className="mt-1 text-[11px] text-muted-foreground">{formatDate(passport.updatedAt, true)}</div></div></div></div>
      </aside>
    </div>
  </div>;
}

function EditFields({ draft, setDraft, onCancel, onSave, saving }: { draft: PassportUpdate; setDraft: (value: PassportUpdate) => void; onCancel: () => void; onSave: () => void; saving: boolean }) {
  const field = (key: keyof PassportUpdate, label: string) => <label className="block"><span className="font-mono-ui text-[9px] uppercase tracking-[.16em] text-muted-foreground">{label}</span><input value={String(draft[key] || '')} onChange={(event) => setDraft({ ...draft, [key]: event.target.value })} className="mt-2 h-10 w-full rounded-xl border border-input bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-accent" data-testid={`input-edit-${String(key)}`} /></label>;
  return <div className="grid gap-4 sm:grid-cols-2">{field('product', 'Product')}{field('brand', 'Brand')}{field('model', 'Model')}{field('serialNumber', 'Serial number')}{field('category', 'Category')}{field('seller', 'Seller')}{field('warranty', 'Warranty')}{field('customerName', 'Customer')}<div className="flex gap-2 sm:col-span-2"><Button variant="secondary" onClick={onCancel} data-testid="button-cancel-edit">Cancel</Button><Button onClick={onSave} disabled={saving} data-testid="button-save-passport">{saving && <LoaderCircle className="animate-spin" size={14} />} Save changes</Button></div></div>;
}

function FileDrop({ label, hint, onFile, capture }: { label: string; hint: string; onFile: (file: File) => void; capture?: boolean }) {
  const ref = useRef<HTMLInputElement>(null);
  return <button type="button" onClick={() => ref.current?.click()} className="group w-full rounded-2xl border border-dashed border-border bg-secondary/45 p-8 text-center transition hover:border-accent hover:bg-accent/10 focus-visible:ring-2 focus-visible:ring-accent" data-testid={`button-upload-${label.toLowerCase().replaceAll(' ', '-')}`}>
    <input ref={ref} type="file" accept={capture ? 'image/*' : '.pdf,.png,.jpg,.jpeg'} capture={capture ? 'environment' : undefined} className="hidden" onChange={(event) => { const file = event.target.files?.[0]; if (file) onFile(file); }} data-testid={`input-file-${label.toLowerCase().replaceAll(' ', '-')}`} />
    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-card text-primary shadow-sm transition group-hover:scale-105">{capture ? <Camera size={22} /> : <CloudUpload size={22} />}</div><div className="mt-4 text-sm font-semibold">{label}</div><div className="mt-1 text-xs text-muted-foreground">{hint}</div>
  </button>;
}

function fileToDataUrl(file: File) {
  return new Promise<string>((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(String(reader.result)); reader.onerror = reject; reader.readAsDataURL(file); });
}

function CreatePassport() {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState<{ name: string; type: string; content: string } | null>(null);
  const [physicalFile, setPhysicalFile] = useState<{ name: string; type: string; content: string } | null>(null);
  const [analysis, setAnalysis] = useState<{ documentType: string; products: DetectedProduct[]; extractedFields?: Record<string, string | number | null> } | null>(null);
  const [physicalResult, setPhysicalResult] = useState<ProductIdentification | null>(null);
  const [autoVerify, setAutoVerify] = useState(true);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [form, setForm] = useState<Partial<PassportInput>>({});
  const [created, setCreated] = useState<Passport | null>(null);

  const analyze = useAnalyzeDocument();
  const identify = useIdentifyProduct();
  const create = useCreatePassport();
  const client = useQueryClient();

  const onDocFile = async (next: File) => {
    setFile({ name: next.name, type: next.type || 'application/octet-stream', content: await fileToDataUrl(next) });
  };

  const onPhysicalFile = async (next: File) => {
    setPhysicalFile({ name: next.name, type: next.type || 'image/jpeg', content: await fileToDataUrl(next) });
  };

  const runAnalysis = () => {
    if (!file) return;
    setStep(2);

    analyze.mutate(
      { data: { fileName: file.name, fileType: file.type, content: file.content } },
      {
        onSuccess: (result) => {
          setAnalysis(result);
          const product = result.products?.[0];
          setForm({
            product: product?.product || '',
            brand: product?.brand || '',
            model: product?.model || '',
            serialNumber: product?.serialNumber || '',
            category: product?.category || '',
            documentType: result.documentType || 'Product document',
            purchaseDate: String(result.extractedFields?.purchaseDate || ''),
            purchasePrice: Number(result.extractedFields?.purchasePrice || 0) || null,
            currency: String(result.extractedFields?.currency || 'USD'),
            warranty: String(result.extractedFields?.warranty || '') || null,
            seller: String(result.extractedFields?.seller || '') || null,
            sourceDocument: file.name,
          });

          if (physicalFile) {
            identify.mutate(
              { data: { image: physicalFile.content } },
              {
                onSuccess: (identRes) => {
                  setPhysicalResult(identRes);
                  setStep(3);
                },
                onError: () => {
                  setStep(3);
                },
              }
            );
          } else {
            setStep(3);
          }
        },
      }
    );
  };

  const createRecord = () => {
    const isPhysicalAttached = Boolean(physicalFile && autoVerify);
    const payload: PassportInput = {
      product: form.product || '',
      brand: form.brand || '',
      model: form.model || '',
      serialNumber: form.serialNumber || '',
      category: form.category || '',
      documentType: form.documentType || 'Product document',
      purchaseDate: form.purchaseDate || null,
      purchasePrice: form.purchasePrice || null,
      currency: form.currency || 'USD',
      warranty: form.warranty || null,
      seller: form.seller || null,
      customerName: form.customerName || null,
      orderId: form.orderId || null,
      invoiceNumber: form.invoiceNumber || null,
      sourceDocument: form.sourceDocument || file?.name || null,
      physicalProductImage: isPhysicalAttached ? physicalFile?.content : null,
      physicalScanDate: isPhysicalAttached ? new Date().toISOString() : null,
      matchConfidence: isPhysicalAttached ? (physicalResult?.confidence || 0.95) : null,
      verificationStatus: isPhysicalAttached ? 'verified' : 'pending',
    };

    create.mutate(
      { data: payload },
      {
        onSuccess: (result) => {
          client.invalidateQueries({ queryKey: getListPassportsQueryKey() });
          client.invalidateQueries({ queryKey: getGetDashboardSummaryQueryKey() });
          client.invalidateQueries({ queryKey: getListActivityQueryKey() });
          setCreated(result);
          setStep(4);
        },
      }
    );
  };

  const updateForm = (key: keyof PassportInput, value: string) =>
    setForm({ ...form, [key]: key === 'purchasePrice' ? Number(value) : value });

  const stepNames = ['Upload', 'Analyze', 'Review', 'Created'];
  const hasPhysical = Boolean(physicalFile && physicalResult);

  return (
    <div className="mx-auto max-w-[1100px]">
      <PageIntro
        eyebrow="Create passport"
        title="Turn evidence into identity."
        description="Upload a product document and physical scan together to verify your product in a single step."
      />

      <div className="mb-8 flex items-center gap-2 overflow-x-auto pb-2">
        {stepNames.map((name, index) => (
          <div key={name} className="flex min-w-max items-center gap-2">
            <div
              className={cx(
                'flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold',
                step > index + 1 ? 'bg-teal-100 text-teal-700' : step === index + 1 ? 'bg-primary text-primary-foreground' : 'bg-secondary text-muted-foreground'
              )}
            >
              {step > index + 1 ? <Check size={14} /> : index + 1}
            </div>
            <span className={cx('text-xs font-semibold', step === index + 1 ? 'text-foreground' : 'text-muted-foreground')}>
              {name}
            </span>
            {index < 3 && <div className="mx-1 h-px w-8 bg-border sm:w-16" />}
          </div>
        ))}
      </div>

      {step === 1 && (
        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          <div className="rounded-2xl border border-border bg-card p-5 md:p-8">
            <div className="mb-6">
              <h2 className="font-display text-2xl font-semibold">Start with a source</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Upload your document and physical product photo together to create and verify your identity in a single step.
              </p>
            </div>

            {/* ⚡ 1-Click Judge Demo Presets Bar */}
            <div className="mb-6 rounded-2xl border border-dashed border-accent/40 bg-accent/5 p-4">
              <div className="flex items-center justify-between gap-2">
                <span className="flex items-center gap-1.5 font-mono-ui text-[11px] font-semibold uppercase tracking-[.14em] text-accent">
                  <Sparkles size={14} className="animate-pulse" /> ⚡ 1-Click Demo Presets
                </span>
                <span className="text-[10px] text-muted-foreground">Click any preset to auto-load document & photo</span>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
                {DEMO_PRESETS.map((preset) => (
                  <button
                    key={preset.id}
                    type="button"
                    onClick={() => {
                      setFile({ name: preset.docName, type: 'image/png', content: preset.docContent });
                      setPhysicalFile({ name: preset.photoName, type: 'image/png', content: preset.photoContent });
                    }}
                    className="flex flex-col items-start rounded-xl border border-border/70 bg-card/90 p-2.5 text-left transition hover:border-accent hover:bg-accent/15"
                    data-testid={`button-preset-${preset.id}`}
                  >
                    <span className="text-base">{preset.icon}</span>
                    <span className="mt-1 line-clamp-1 text-xs font-semibold text-foreground">{preset.title}</span>
                    <span className="text-[9px] text-muted-foreground">{preset.badge}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <div className="space-y-2">
                <span className="flex items-center gap-1.5 font-mono-ui text-[10px] font-semibold uppercase tracking-[.14em] text-primary">
                  <FileText size={13} /> 1. Purchase Document (Required)
                </span>
                <FileDrop
                  label={file ? file.name : 'Upload a document'}
                  hint={file ? 'Ready to analyze' : 'Invoice, receipt, warranty (PDF, JPG, PNG)'}
                  onFile={onDocFile}
                />
                {file && (
                  <div className="flex items-center justify-between rounded-xl border border-teal-200 bg-teal-50 px-3 py-2 text-xs text-teal-800">
                    <span className="flex items-center gap-2 truncate">
                      <FileCheck2 size={14} className="shrink-0" /> {file.name}
                    </span>
                    <button onClick={() => setFile(null)} aria-label="Remove source document" data-testid="button-remove-source">
                      <X size={14} />
                    </button>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <span className="flex items-center gap-1.5 font-mono-ui text-[10px] font-semibold uppercase tracking-[.14em] text-accent">
                  <Camera size={13} /> 2. Physical Product Photo (Optional)
                </span>
                <FileDrop
                  label={physicalFile ? physicalFile.name : 'Upload product photo'}
                  hint={physicalFile ? 'Product photo attached' : 'Device photo or camera capture (JPG, PNG)'}
                  onFile={onPhysicalFile}
                  capture
                />
                {physicalFile && (
                  <div className="flex items-center justify-between rounded-xl border border-accent/40 bg-accent/15 px-3 py-2 text-xs text-primary">
                    <span className="flex items-center gap-2 truncate">
                      <ImageIcon size={14} className="shrink-0" /> {physicalFile.name}
                    </span>
                    <button onClick={() => setPhysicalFile(null)} aria-label="Remove product photo" data-testid="button-remove-physical">
                      <X size={14} />
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div className="mt-6 rounded-xl border border-border bg-secondary/50 p-4">
              <div className="flex items-start gap-3">
                <ShieldCheck size={18} className="mt-0.5 shrink-0 text-teal-600" />
                <div className="text-xs leading-relaxed text-muted-foreground">
                  <span className="font-semibold text-foreground">Dual-Evidence Verification:</span> Providing both documents and photos allows Verid to extract warranty data and confirm the physical device with YOLO in one unified pass.
                </div>
              </div>
            </div>

            <Button
              className="mt-6 w-full"
              disabled={!file}
              onClick={runAnalysis}
              data-testid="button-analyze-document"
            >
              <Sparkles size={15} /> {physicalFile ? 'Analyze Document & Verify Physical Product' : 'Analyze Document'}
            </Button>
          </div>

          <ProcessAside
            title="What happens next"
            items={[
              'Document OCR extracts brand, model, serial, and dates',
              physicalFile ? 'YOLO identifies the physical device from your photo' : 'You can optionally add a physical photo later',
              'Review and verify everything together before saving',
            ]}
          />
        </div>
      )}

      {step === 2 && (
        <div className="rounded-2xl border border-border bg-card p-10 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-accent/20 text-primary">
            <Sparkles size={24} className="animate-spin" />
          </div>
          <h2 className="mt-5 font-display text-2xl font-semibold">Reading your evidence</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {physicalFile
              ? 'Extracting document details via RapidOCR and scanning physical photo with YOLO…'
              : 'Finding product signals and purchase details…'}
          </p>
          <div className="mx-auto mt-7 max-w-sm space-y-2 text-left">
            <div className="skeleton h-3 rounded-full" />
            <div className="skeleton h-3 w-4/5 rounded-full" />
            <div className="skeleton h-3 w-3/5 rounded-full" />
          </div>
          {analyze.isError && (
            <div className="mt-6">
              <ErrorState label="The document could not be analyzed." onRetry={runAnalysis} />
            </div>
          )}
        </div>
      )}

      {step === 3 && (
        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          <div className="rounded-2xl border border-border bg-card p-5 md:p-8">
            <div className="mb-6 flex items-start justify-between">
              <div>
                <h2 className="font-display text-2xl font-semibold">Review the record</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Make sure these details match your sources before creating.
                </p>
              </div>
              <StatusPill
                status={hasPhysical && autoVerify ? 'verified' : 'pending'}
                label={hasPhysical && autoVerify ? 'Direct verification' : 'Review required'}
              />
            </div>

            {analysis?.products?.length ? (
              <div className="mb-6 flex gap-2 overflow-x-auto pb-1">
                {analysis.products.map((product, index) => (
                  <button
                    key={`${product.product}-${index}`}
                    onClick={() => {
                      setSelectedIndex(index);
                      setForm({
                        ...form,
                        product: product.product,
                        brand: product.brand,
                        model: product.model,
                        serialNumber: product.serialNumber,
                        category: product.category,
                      });
                    }}
                    className={cx(
                      'min-w-[180px] rounded-xl border p-3 text-left transition',
                      selectedIndex === index ? 'border-primary bg-secondary' : 'border-border hover:border-accent'
                    )}
                    data-testid={`button-detected-product-${index}`}
                  >
                    <div className="text-xs font-semibold">{product.product}</div>
                    <div className="mt-1 text-[11px] text-muted-foreground">
                      {product.brand} · {product.model}
                    </div>
                  </button>
                ))}
              </div>
            ) : null}

            <div className="grid gap-4 sm:grid-cols-2">
              {(
                [
                  'product',
                  'brand',
                  'model',
                  'serialNumber',
                  'category',
                  'documentType',
                  'purchaseDate',
                  'seller',
                  'invoiceNumber',
                  'orderId',
                ] as Array<keyof PassportInput>
              ).map((key) => (
                <label key={key} className="block">
                  <span className="font-mono-ui text-[9px] uppercase tracking-[.16em] text-muted-foreground">
                    {key.replace(/([A-Z])/g, ' $1')}
                  </span>
                  <input
                    value={String(form[key] ?? '')}
                    onChange={(event) => updateForm(key, event.target.value)}
                    className="mt-2 h-10 w-full rounded-xl border border-input bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-accent"
                    data-testid={`input-create-${String(key)}`}
                  />
                </label>
              ))}
            </div>

            <div className="mt-6 flex gap-2">
              <Button variant="secondary" onClick={() => setStep(1)} data-testid="button-back-upload">
                <ArrowLeft size={14} /> Back
              </Button>
              <Button
                onClick={createRecord}
                disabled={create.isPending || !form.product}
                data-testid="button-create-passport"
              >
                {create.isPending && <LoaderCircle className="animate-spin" size={14} />}
                {hasPhysical && autoVerify ? 'Create & Verify Passport' : 'Create passport'} <ArrowRight size={14} />
              </Button>
            </div>

            {create.isError && (
              <p className="mt-3 text-xs text-red-600" data-testid="text-create-error">
                Could not create this passport. Check the required fields and try again.
              </p>
            )}
          </div>

          <aside className="space-y-4">
            {physicalFile && (
              <div className="rounded-2xl border border-border bg-card p-5">
                <div className="flex items-center justify-between">
                  <h3 className="font-display text-sm font-semibold">Physical Verification</h3>
                  <StatusPill
                    status={physicalResult?.confidence ? 'verified' : 'pending'}
                    label={physicalResult?.confidence ? `${Math.round(physicalResult.confidence * 100)}% match` : 'Scanned'}
                  />
                </div>

                <div className="relative mt-3 overflow-hidden rounded-xl bg-primary/5">
                  <img
                    src={physicalFile.content}
                    alt="Physical scan preview"
                    className="h-36 w-full object-contain"
                  />
                  {physicalResult?.boundingBox && physicalResult.boundingBox.length === 4 && (
                    <div
                      className="absolute rounded border-2 border-accent bg-accent/20 transition-all pointer-events-none"
                      style={{
                        top: `${physicalResult.boundingBox[0] * 100}%`,
                        left: `${physicalResult.boundingBox[1] * 100}%`,
                        height: `${Math.max(12, (physicalResult.boundingBox[2] - physicalResult.boundingBox[0]) * 100)}%`,
                        width: `${Math.max(12, (physicalResult.boundingBox[3] - physicalResult.boundingBox[1]) * 100)}%`,
                      }}
                    >
                      <span className="absolute -top-5 left-0 rounded bg-accent px-1.5 py-0.5 text-[9px] font-bold text-accent-foreground shadow-sm">
                        {physicalResult.detectedProduct} · {Math.round((physicalResult.confidence || 0.95) * 100)}%
                      </span>
                    </div>
                  )}
                </div>

                {physicalResult && (
                  <div className="mt-3 space-y-2 text-xs">
                    <div className="flex justify-between text-muted-foreground">
                      <span>Detected:</span>
                      <span className="font-semibold text-foreground">{physicalResult.detectedProduct}</span>
                    </div>
                    <div className="flex justify-between text-muted-foreground">
                      <span>Form factor:</span>
                      <span className="font-semibold text-foreground">{physicalResult.category}</span>
                    </div>
                  </div>
                )}

                <label className="mt-4 flex cursor-pointer items-center gap-2 rounded-xl bg-secondary p-3 text-xs">
                  <input
                    type="checkbox"
                    checked={autoVerify}
                    onChange={(e) => setAutoVerify(e.target.checked)}
                    className="rounded text-primary focus:ring-accent"
                  />
                  <span className="font-medium text-foreground">Attach scan and verify identity now</span>
                </label>
              </div>
            )}

            <ProcessAside
              title="Source notes"
              items={[
                `Document type: ${analysis?.documentType || 'Detected'}`,
                `${analysis?.products?.length || 0} product signal${analysis?.products?.length === 1 ? '' : 's'} found`,
                physicalFile ? 'Physical product photo will be permanently linked' : 'You can link physical photos later via Scan Product',
              ]}
            />
          </aside>
        </div>
      )}

      {step === 4 && created && (
        <div className="mx-auto max-w-[650px] rounded-2xl border border-border bg-card p-8 text-center md:p-12">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-teal-100 text-teal-700">
            <Check size={30} />
          </div>
          <div className="mt-6 font-mono-ui text-[10px] uppercase tracking-[.2em] text-teal-700">
            {created.verificationStatus === 'verified' ? 'Passport Created & Physically Verified' : 'Passport Created'}
          </div>
          <h2 className="mt-2 font-display text-3xl font-semibold">{created.product}</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {created.verificationStatus === 'verified'
              ? 'Your product identity is verified with physical scan evidence attached.'
              : 'The record is ready to verify and share with your team.'}
          </p>

          <div className="mx-auto mt-6 max-w-xs rounded-xl bg-secondary p-3 text-left">
            <div className="font-mono-ui text-[9px] uppercase tracking-[.16em] text-muted-foreground">Passport ID</div>
            <div className="mt-1 font-mono-ui text-sm font-medium" data-testid="text-created-passport-id">
              {created.passportId}
            </div>
            {created.physicalScanDate && (
              <div className="mt-2 flex items-center gap-1.5 text-[11px] text-teal-700">
                <BadgeCheck size={14} /> Physically verified
              </div>
            )}
          </div>

          <div className="mt-7 flex flex-col justify-center gap-2 sm:flex-row">
            <Link
              href={`/passports/${created.passportId}`}
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-primary px-4 text-sm font-semibold text-primary-foreground"
              data-testid="link-open-created-passport"
            >
              Open passport <ArrowRight size={14} />
            </Link>
            <Link
              href="/create"
              onClick={() => {
                setStep(1);
                setFile(null);
                setPhysicalFile(null);
                setAnalysis(null);
                setPhysicalResult(null);
                setCreated(null);
                setForm({});
              }}
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl border border-border px-4 text-sm font-semibold"
              data-testid="link-create-another"
            >
              Create another
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

function ProcessAside({ title, items }: { title: string; items: string[] }) {
  return <aside className="rounded-2xl border border-border bg-secondary/65 p-5"><div className="flex items-center gap-2 text-xs font-semibold"><ShieldCheck size={15} className="text-primary" /> {title}</div><div className="mt-5 space-y-4">{items.map((item, index) => <div className="flex gap-3" key={item}><div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-card font-mono-ui text-[10px] text-primary">{index + 1}</div><p className="text-xs leading-relaxed text-muted-foreground">{item}</p></div>)}</div></aside>;
}

function Scan() {
  const [image, setImage] = useState('');
  const [imageName, setImageName] = useState('');
  const [identified, setIdentified] = useState<ProductIdentification | null>(null);
  const [matches, setMatches] = useState<{ matches: ProductMatch[] } | null>(null);
  const identify = useIdentifyProduct();
  const match = useMatchProduct();
  const link = useLinkProduct();
  const client = useQueryClient();

  const onFile = async (file: File) => {
    setImage(await fileToDataUrl(file));
    setImageName(file.name);
    setIdentified(null);
    setMatches(null);
  };

  const loadPreset = (preset: typeof DEMO_PRESETS[0]) => {
    setImage(preset.photoContent);
    setImageName(preset.photoName);
    setIdentified(null);
    setMatches(null);
  };

  const identifyNow = () => {
    if (!image) return;
    identify.mutate(
      { data: { image } },
      {
        onSuccess: (result) => {
          setIdentified(result);
          match.mutate({ data: { detectedProduct: result } }, { onSuccess: setMatches });
        },
      }
    );
  };

  return (
    <div className="mx-auto max-w-[1100px]">
      <PageIntro
        eyebrow="Scan product"
        title="Find the record in the room."
        description="Use a product photo to identify physical details, compare them to your registry, and link the right passport."
      />

      <div className="mb-8 flex items-center gap-2">
        <StepBadge active={!identified} done={Boolean(identified)} label="Capture" number="01" />
        <div className="h-px w-10 bg-border" />
        <StepBadge active={Boolean(identified) && !matches} done={Boolean(matches)} label="Match" number="02" />
        <div className="h-px w-10 bg-border" />
        <StepBadge active={Boolean(matches)} label="Link" number="03" />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="rounded-2xl border border-border bg-card p-5 md:p-8">
          {/* Quick Demo Presets Bar */}
          <div className="mb-6 rounded-2xl border border-dashed border-accent/40 bg-accent/5 p-4">
            <div className="flex items-center justify-between gap-2">
              <span className="flex items-center gap-1.5 font-mono-ui text-[11px] font-semibold uppercase tracking-[.14em] text-accent">
                <Sparkles size={14} className="animate-pulse" /> ⚡ 1-Click Scan Samples
              </span>
              <span className="text-[10px] text-muted-foreground">Test live detection without uploading</span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
              {DEMO_PRESETS.map((preset) => (
                <button
                  key={preset.id}
                  type="button"
                  onClick={() => loadPreset(preset)}
                  className="flex flex-col items-start rounded-xl border border-border/70 bg-card/90 p-2.5 text-left transition hover:border-accent hover:bg-accent/15"
                  data-testid={`button-scan-preset-${preset.id}`}
                >
                  <span className="text-base">{preset.icon}</span>
                  <span className="mt-1 line-clamp-1 text-xs font-semibold text-foreground">{preset.title}</span>
                  <span className="text-[9px] text-muted-foreground">{preset.badge}</span>
                </button>
              ))}
            </div>
          </div>

          {!image ? (
            <div className="grid gap-4 sm:grid-cols-2">
              <FileDrop label="Upload a product photo" hint="JPG, PNG, or HEIC" onFile={onFile} capture />
              <FileDrop label="Take a photo" hint="Use your device camera" onFile={onFile} capture />
            </div>
          ) : (
            <>
              <div className="relative overflow-hidden rounded-2xl bg-primary/5">
                {image.startsWith('data:image') ? (
                  <img
                    src={image}
                    alt="Uploaded product"
                    className="h-[280px] w-full object-contain"
                    data-testid="img-scan-preview"
                  />
                ) : (
                  <div className="flex h-[280px] items-center justify-center text-sm text-muted-foreground">
                    <ImageIcon size={20} />
                  </div>
                )}
                {identified?.boundingBox && identified.boundingBox.length === 4 && (
                  <div
                    className="absolute rounded border-2 border-accent bg-accent/20 transition-all pointer-events-none"
                    style={{
                      top: `${identified.boundingBox[0] * 100}%`,
                      left: `${identified.boundingBox[1] * 100}%`,
                      height: `${Math.max(12, (identified.boundingBox[2] - identified.boundingBox[0]) * 100)}%`,
                      width: `${Math.max(12, (identified.boundingBox[3] - identified.boundingBox[1]) * 100)}%`,
                    }}
                  >
                    <span className="absolute -top-5 left-0 rounded bg-accent px-1.5 py-0.5 text-[9px] font-bold text-accent-foreground shadow-sm">
                      {identified.detectedProduct} · {Math.round((identified.confidence || 0.95) * 100)}%
                    </span>
                  </div>
                )}
                <button
                  className="absolute right-3 top-3 rounded-lg bg-card/90 p-2 text-muted-foreground shadow-sm hover:text-red-600"
                  onClick={() => {
                    setImage('');
                    setImageName('');
                    setIdentified(null);
                    setMatches(null);
                  }}
                  aria-label="Remove product image"
                  data-testid="button-remove-scan-image"
                >
                  <X size={15} />
                </button>
              </div>

              <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                <span className="flex items-center gap-2 truncate">
                  <ImageIcon size={13} className="shrink-0" /> {imageName}
                </span>
                <span className="font-mono-ui font-semibold text-accent">READY</span>
              </div>

              {!identified && (
                <Button
                  className="mt-5 w-full"
                  onClick={identifyNow}
                  disabled={identify.isPending}
                  data-testid="button-identify-product"
                >
                  {identify.isPending ? <LoaderCircle className="animate-spin" size={15} /> : <Sparkles size={15} />}
                  {' '}Identify product with YOLO
                </Button>
              )}

              {identify.isError && (
                <p className="mt-3 text-xs text-red-600" data-testid="text-identify-error">
                  We could not read that image. Try a clearer angle.
                </p>
              )}
            </>
          )}
        </div>

        <aside className="space-y-4">
          {identified && (
            <div className="rounded-2xl border border-border bg-card p-5">
              <div className="flex items-center justify-between">
                <h2 className="font-display text-lg font-semibold">Detected signal</h2>
                <StatusPill
                  status={identified.confidence >= 0.8 ? 'high' : 'medium'}
                  label={`${Math.round(identified.confidence * 100)}% match`}
                />
              </div>
              <div className="mt-5 space-y-4">
                <DetailField label="Product" value={identified.detectedProduct} />
                <DetailField label="Category" value={identified.category} />
                <DetailField label="Brand" value={identified.brand || 'Visual detection'} />
                <DetailField label="Detection Source" value={identified.source || 'Fine-tuned YOLO'} mono />
              </div>
              {identified.visualFeatures?.length ? (
                <div className="mt-5 flex flex-wrap gap-1.5">
                  {identified.visualFeatures.map((feature) => (
                    <span key={feature} className="rounded-lg bg-secondary px-2 py-1 text-[10px] text-muted-foreground">
                      {feature}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          )}

          {matches && (
            <div className="rounded-2xl border border-border bg-card p-5">
              <div className="flex items-center gap-2 text-xs font-semibold">
                <Link2 size={15} className="text-accent" /> Matching passports
              </div>
              {matches.matches?.length ? (
                <div className="mt-4 space-y-2">
                  {matches.matches.map((item) => (
                    <div className="rounded-xl border border-border p-3" key={item.passportId}>
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="text-xs font-semibold">{item.passport.product}</div>
                          <div className="mt-1 font-mono-ui text-[10px] text-muted-foreground">
                            {item.passportId}
                          </div>
                        </div>
                        <StatusPill status={item.confidence} label={`${Math.round(item.matchScore * 100)}%`} />
                      </div>
                      <p className="mt-2 text-[11px] leading-relaxed text-muted-foreground">
                        {item.reason?.[0] || 'Signals align with this passport.'}
                      </p>
                      <Button
                        className="mt-3 w-full"
                        onClick={() =>
                          link.mutate(
                            {
                              passportId: item.passportId,
                              data: {
                                image,
                                confidence: item.matchScore,
                                scanDate: new Date().toISOString(),
                              },
                            },
                            {
                              onSuccess: () => {
                                client.invalidateQueries({ queryKey: getGetPassportQueryKey(item.passportId) });
                                client.invalidateQueries({ queryKey: getListPassportsQueryKey() });
                                client.invalidateQueries({ queryKey: getGetDashboardSummaryQueryKey() });
                                client.invalidateQueries({ queryKey: getListActivityQueryKey() });
                              },
                            }
                          )
                        }
                        disabled={link.isPending}
                        data-testid={`button-link-passport-${item.passportId}`}
                      >
                        {link.isPending ? <LoaderCircle className="animate-spin" size={14} /> : <Link2 size={14} />}
                        {' '}Link this passport
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-4 text-xs text-muted-foreground">
                  No close record found. Try another angle or create a new passport.
                </p>
              )}
              {link.isSuccess && (
                <div className="mt-4 flex items-center gap-2 text-xs font-semibold text-teal-700" data-testid="status-link-success">
                  <Check size={14} /> Physical product linked
                </div>
              )}
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

function StepBadge({ active, done, label, number }: { active?: boolean; done?: boolean; label: string; number: string }) {
  return <div className="flex items-center gap-2"><div className={cx('flex h-8 w-8 items-center justify-center rounded-full font-mono-ui text-[10px] font-medium', done ? 'bg-teal-100 text-teal-700' : active ? 'bg-primary text-primary-foreground' : 'bg-secondary text-muted-foreground')}>{done ? <Check size={14} /> : number}</div><span className={cx('text-xs font-semibold', active || done ? 'text-foreground' : 'text-muted-foreground')}>{label}</span></div>;
}

function ActivityItem({ item, dark = false }: { item: { id: string; type: string; title: string; description: string; timestamp: string; passportId?: string | null }; dark?: boolean }) {
  return <div className="flex gap-3" data-testid={`activity-item-${item.id}`}><div className={cx('mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg', dark ? 'bg-primary-foreground/10 text-accent' : 'bg-secondary text-primary')}><ActivityIcon size={13} /></div><div className="min-w-0 flex-1"><div className={cx('text-xs font-semibold', dark ? 'text-primary-foreground' : 'text-foreground')}>{item.title}</div><div className={cx('mt-1 text-[11px] leading-relaxed', dark ? 'text-primary-foreground/55' : 'text-muted-foreground')}>{item.description}</div><div className={cx('mt-1.5 font-mono-ui text-[9px]', dark ? 'text-primary-foreground/35' : 'text-muted-foreground')}>{formatDate(item.timestamp, true)}</div></div></div>;
}

function ActivityPage() {
  const query = useListActivity<Activity[]>({ query: { queryKey: getListActivityQueryKey() } });
  return <div className="mx-auto max-w-[1000px]"><PageIntro eyebrow="Activity history" title="A quiet audit trail." description="Every analysis, match, and update stays visible so your team knows what happened and when." action={<Button variant="secondary" onClick={() => query.refetch()} disabled={query.isFetching} data-testid="button-refresh-activity">{query.isFetching ? <LoaderCircle className="animate-spin" size={14} /> : <RefreshCw size={14} />} Refresh</Button>} />{query.isLoading ? <LoadingBlock rows={6} /> : query.isError ? <ErrorState onRetry={() => query.refetch()} /> : query.data?.length ? <div className="rounded-2xl border border-border bg-card p-5 md:p-7"><div className="mb-5 flex items-center justify-between border-b border-border pb-4"><span className="font-mono-ui text-[10px] uppercase tracking-[.18em] text-muted-foreground">Event</span><span className="font-mono-ui text-[10px] uppercase tracking-[.18em] text-muted-foreground">Timestamp</span></div><div className="space-y-6">{query.data.map((item) => <ActivityItem key={item.id} item={item} />)}</div></div> : <EmptyState icon={ActivityIcon} title="The trail is clear" description="New passport and scan activity will appear here as your workspace changes." />}</div>;
}

function SettingsPage() {
  const status = useGetSystemStatus();
  const [notify, setNotify] = useState(true);
  const [autoVerify, setAutoVerify] = useState(true);
  return <div className="mx-auto max-w-[1000px]"><PageIntro eyebrow="Settings" title="Keep the workspace steady." description="Service health and personal preferences for your product identity workflow." action={<Button variant="secondary" onClick={() => status.refetch()} disabled={status.isFetching} data-testid="button-refresh-status">{status.isFetching ? <LoaderCircle className="animate-spin" size={14} /> : <RefreshCw size={14} />} Check services</Button>} /><div className="grid gap-6 lg:grid-cols-[1.1fr_.9fr]"><section className="rounded-2xl border border-border bg-card p-5 md:p-7"><div className="flex items-center gap-3"><div className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-primary"><ShieldCheck size={19} /></div><div><h2 className="font-display text-xl font-semibold">Service status</h2><p className="mt-1 text-xs text-muted-foreground">Live connectivity for Verid services.</p></div></div>{status.isLoading ? <div className="mt-7"><LoadingBlock rows={3} /></div> : status.isError ? <div className="mt-7"><ErrorState onRetry={() => status.refetch()} label="Service status is temporarily unavailable." /></div> : <div className="mt-7 space-y-3"><ServiceRow service={status.data?.backend} /><div className="my-5 h-px bg-border" />{status.data?.services?.map((service) => <ServiceRow service={service} key={service.name} />)}</div>}</section><section className="rounded-2xl border border-border bg-card p-5 md:p-7"><div className="flex items-center gap-3"><div className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-primary"><Settings2 size={19} /></div><div><h2 className="font-display text-xl font-semibold">Preferences</h2><p className="mt-1 text-xs text-muted-foreground">Tune how your team works with identity records.</p></div></div><div className="mt-7 space-y-1"><PreferenceRow label="Activity notifications" description="Show updates when records are changed." value={notify} onChange={setNotify} testId="switch-notifications" /><PreferenceRow label="Auto-suggest verification" description="Surface high-confidence matches first." value={autoVerify} onChange={setAutoVerify} testId="switch-auto-verify" /></div><div className="mt-7 rounded-xl bg-secondary p-4"><div className="flex items-center gap-2 text-xs font-semibold"><Tag size={14} className="text-primary" /> Workspace identity</div><p className="mt-2 text-xs leading-relaxed text-muted-foreground">You are working in <span className="font-semibold text-foreground">Alex Morgan’s operations team</span>. Preferences are saved for this device.</p></div></section></div></div>;
}

function ServiceRow({ service }: { service?: { name: string; status: string; detail: string } }) {
  if (!service) return null;
  return <div className="flex items-center justify-between gap-4" data-testid={`service-row-${service.name.toLowerCase().replaceAll(' ', '-')}`}><div className="min-w-0"><div className="text-sm font-semibold">{service.name}</div><div className="mt-1 truncate text-xs text-muted-foreground">{service.detail}</div></div><StatusPill status={service.status} /></div>;
}

function PreferenceRow({ label, description, value, onChange, testId }: { label: string; description: string; value: boolean; onChange: (value: boolean) => void; testId: string }) {
  return <div className="flex items-center justify-between gap-4 border-b border-border py-4 last:border-0"><div><div className="text-sm font-semibold">{label}</div><div className="mt-1 text-xs text-muted-foreground">{description}</div></div><button role="switch" aria-checked={value} onClick={() => onChange(!value)} className={cx('relative h-6 w-11 shrink-0 rounded-full transition-colors', value ? 'bg-primary' : 'bg-muted')} data-testid={testId}><span className={cx('absolute top-1 h-4 w-4 rounded-full bg-card shadow-sm transition-transform', value ? 'translate-x-6' : 'translate-x-1')} /></button></div>;
}

function Router() {
  const [location] = useLocation();
  return <ErrorBoundary resetKey={location}><Shell><Switch><Route path="/" component={Dashboard} /><Route path="/passports" component={Passports} /><Route path="/passports/:passportId" component={PassportDetail} /><Route path="/create" component={CreatePassport} /><Route path="/scan" component={Scan} /><Route path="/activity" component={ActivityPage} /><Route path="/settings" component={SettingsPage} /><Route component={NotFound} /></Switch></Shell></ErrorBoundary>;
}

export default function App() {
  return <QueryClientProvider client={queryClient}><WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}><Router /></WouterRouter></QueryClientProvider>;
}