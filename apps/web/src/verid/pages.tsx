import { useState } from 'react';
import { Link, useParams } from 'wouter';
import { ArrowLeft, Camera, FileText, MapPin } from 'lucide-react';
import { askHousehold } from '@/lib/household';
import { fetchGraph, fetchNotices, fetchProductMemory, fetchRooms, placeProduct, type GraphNode } from './memory-api';
import { QuietLine, useAsync } from './shell';

function daysLabel(days: number | null) {
  if (days === null) return 'Warranty unknown';
  if (days < 0) return `Expired ${Math.abs(days)} days ago`;
  return `${days} days of warranty left`;
}

export function HomePage() {
  const graph = useAsync(fetchGraph, []);
  const notices = useAsync(fetchNotices, []);
  const first = notices.data?.notices[0];
  const count = graph.data?.nodes.length ?? 0;

  return (
    <div className="page-enter">
      <p className="font-mono-ui text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Home</p>
      <h1 className="mt-3 font-display text-[34px] font-semibold leading-[1.1] tracking-[-0.04em] md:text-[42px]">
        Your phone remembers everything you own.
      </h1>
      <div className="mt-4">
        <QuietLine>
          {graph.loading
            ? 'Reading the household vault…'
            : count
              ? `${count} products are in memory. You confirm. Verid remembers.`
              : 'Nothing remembered yet. Add an invoice and one photo — Verid will try to understand the rest.'}
        </QuietLine>
      </div>

      {first && (
        <Link href={first.href} className="mt-10 block border-t border-border pt-6" data-testid="notice-primary">
          <div className="text-[12px] font-medium uppercase tracking-[0.14em] text-muted-foreground">Quietly noticed</div>
          <div className="mt-2 text-lg font-semibold tracking-tight">{first.title}</div>
          <p className="mt-1 text-sm text-muted-foreground">{first.detail}</p>
        </Link>
      )}

      <section className="mt-12">
        <div className="text-[12px] font-medium uppercase tracking-[0.14em] text-muted-foreground">Rooms</div>
        <div className="mt-4 divide-y divide-border">
          {(graph.data?.byRoom || [])
            .filter((group) => group.items.length > 0)
            .map((group) => (
              <Link key={group.room.id} href="/memory" className="flex items-baseline justify-between py-3.5">
                <span className="text-[16px]">{group.room.name}</span>
                <span className="text-sm text-muted-foreground">{group.items.length}</span>
              </Link>
            ))}
        </div>
      </section>

      <div className="mt-12 flex flex-wrap gap-3">
        <Link href="/remember" className="rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground">
          Remember something
        </Link>
        <Link href="/camera" className="rounded-full border border-border px-5 py-2.5 text-sm font-semibold">
          Point the camera
        </Link>
      </div>
    </div>
  );
}

export function MemoryPage() {
  const graph = useAsync(fetchGraph, []);
  const [q, setQ] = useState('');
  const query = q.trim().toLowerCase();

  return (
    <div className="page-enter">
      <p className="font-mono-ui text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Memory</p>
      <h1 className="mt-3 font-display text-3xl font-semibold tracking-[-0.04em]">Everything Verid remembers</h1>
      <input
        value={q}
        onChange={(event) => setQ(event.target.value)}
        placeholder="Search a product, room, serial…"
        className="mt-6 h-12 w-full border-b border-border bg-transparent text-[16px] outline-none"
        data-testid="input-memory-search"
      />
      {graph.loading && <p className="mt-10 text-sm text-muted-foreground">Loading memory…</p>}
      {(graph.data?.byRoom || []).map((group) => {
        const items = group.items.filter((node) => {
          if (!query) return true;
          const blob = `${node.passport.product} ${node.passport.brand} ${node.passport.model} ${node.passport.serialNumber} ${group.room.name}`.toLowerCase();
          return blob.includes(query);
        });
        if (!items.length) return null;
        return (
          <section key={group.room.id} className="mt-12">
            <h2 className="font-display text-xl font-semibold">{group.room.name}</h2>
            <div className="mt-3 divide-y divide-border">
              {items.map((node) => (
                <MemoryRow key={node.passport.passportId} node={node} />
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}

function MemoryRow({ node }: { node: GraphNode }) {
  return (
    <Link href={`/memory/${node.passport.passportId}`} className="flex items-start justify-between gap-4 py-4" data-testid={`memory-${node.passport.passportId}`}>
      <div>
        <div className="text-[16px] font-medium">{node.passport.product}</div>
        <div className="mt-1 text-sm text-muted-foreground">
          {node.passport.brand}
          {node.memory.locationNote ? ` · ${node.memory.locationNote}` : ''}
        </div>
        {node.missing.length > 0 && (
          <div className="mt-1 text-[12px] text-muted-foreground">Still unknown: {node.missing.join(', ')}</div>
        )}
      </div>
      <div className="shrink-0 text-right text-[12px] text-muted-foreground">{daysLabel(node.warrantyDaysLeft)}</div>
    </Link>
  );
}

export function ProductMemoryPage() {
  const { passportId = '' } = useParams<{ passportId: string }>();
  const product = useAsync(() => fetchProductMemory(passportId), [passportId]);
  const rooms = useAsync(fetchRooms, []);
  const node = product.data;
  const [note, setNote] = useState('');
  const [roomId, setRoomId] = useState('');

  if (product.loading) return <p className="text-sm text-muted-foreground">Opening memory…</p>;
  if (!node) return <p className="text-sm text-muted-foreground">This product is not in memory.</p>;

  const savePlace = async () => {
    await placeProduct(node.passport.passportId, roomId || node.memory.roomId, note || node.memory.locationNote);
    window.location.reload();
  };

  return (
    <div className="page-enter">
      <Link href="/memory" className="inline-flex items-center gap-1 text-sm text-muted-foreground">
        <ArrowLeft size={14} /> Memory
      </Link>
      <h1 className="mt-5 font-display text-[32px] font-semibold tracking-[-0.04em]">{node.passport.product}</h1>
      <p className="mt-2 text-muted-foreground">
        {node.passport.brand} · {node.room?.name || 'Not placed'}
        {node.memory.locationNote ? ` — ${node.memory.locationNote}` : ''}
      </p>
      <p className="mt-1 text-[12px] text-muted-foreground">
        Location is {node.memory.lastSeenConfidence}. Not GPS.
      </p>

      <dl className="mt-10 grid gap-6 sm:grid-cols-2">
        <Field label="Model" value={node.passport.model} evidence={node.evidence.model} />
        <Field label="Serial" value={node.passport.serialNumber} evidence={node.evidence.serial} />
        <Field label="Purchased" value={node.passport.purchaseDate} evidence={node.evidence.warranty} />
        <Field label="Warranty" value={`${node.passport.warranty || '—'} · ${daysLabel(node.warrantyDaysLeft)}`} evidence={node.evidence.warranty} />
        <Field label="Retailer" value={node.passport.seller} />
        <Field label="Document" value={node.passport.sourceDocument} />
      </dl>

      <div className="mt-10 flex flex-wrap gap-2">
        <Link href="/ask" className="rounded-full border border-border px-4 py-2 text-sm">Ask</Link>
        <Link href="/camera" className="rounded-full border border-border px-4 py-2 text-sm">See it</Link>
        <button
          type="button"
          className="rounded-full border border-border px-4 py-2 text-sm"
          onClick={async () => {
            const pack = await fetch(`/api/passport/${node.passport.passportId}/claim-pack`);
            const data = await pack.json();
            const win = window.open('', '_blank');
            if (!win) return;
            win.document.write(`<pre style="font:14px/1.5 system-ui;padding:24px">${JSON.stringify(data.fields, null, 2)}\n\nSHA-256 ${data.seal}</pre>`);
            win.print();
          }}
        >
          Claim pack
        </button>
      </div>

      <section className="mt-14">
        <h2 className="font-display text-lg font-semibold">Where is it?</h2>
        <QuietLine>Confirm a room. Verid will not guess a floor plan.</QuietLine>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <select
            className="h-11 flex-1 rounded-xl border border-border bg-background px-3 text-sm"
            defaultValue={node.memory.roomId || ''}
            onChange={(event) => setRoomId(event.target.value)}
          >
            <option value="">Not placed yet</option>
            {(rooms.data?.rooms || []).filter((room) => room.id !== 'unplaced').map((room) => (
              <option key={room.id} value={room.id}>{room.name}</option>
            ))}
          </select>
          <input
            className="h-11 flex-1 rounded-xl border border-border bg-background px-3 text-sm"
            placeholder="Near the desk, left wall…"
            defaultValue={node.memory.locationNote}
            onChange={(event) => setNote(event.target.value)}
          />
          <button type="button" onClick={() => void savePlace()} className="h-11 rounded-xl bg-primary px-4 text-sm font-semibold text-primary-foreground">
            Confirm location
          </button>
        </div>
      </section>
    </div>
  );
}

function Field({ label, value, evidence }: { label: string; value?: string | null; evidence?: string }) {
  return (
    <div>
      <dt className="text-[11px] uppercase tracking-[0.14em] text-muted-foreground">{label}</dt>
      <dd className="mt-1 text-[16px]">{value || 'Unknown'}</dd>
      {evidence && <p className="mt-1 text-[12px] text-muted-foreground">{evidence}</p>}
    </div>
  );
}

export function AskPage() {
  const [value, setValue] = useState('');
  const [busy, setBusy] = useState(false);
  const [reply, setReply] = useState<{ answer: string; why?: string; sources?: Array<{ passportId?: string; field?: string }>; engine?: string } | null>(null);

  const run = async (question: string) => {
    const q = question.trim();
    if (!q) return;
    setValue(q);
    setBusy(true);
    try {
      setReply(await askHousehold(q));
    } finally {
      setBusy(false);
    }
  };

  const prompts = [
    'How much longer is my refrigerator warranty?',
    'Where is the laptop?',
    'Which appliances are still under warranty?',
    'Where is the original invoice for the washing machine?',
    'What needs attention?',
  ];

  return (
    <div className="page-enter">
      <p className="font-mono-ui text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Ask Verid</p>
      <h1 className="mt-3 font-display text-3xl font-semibold tracking-[-0.04em]">Ask anything you would otherwise have to remember.</h1>
      <div className="mt-8 flex gap-2 border-b border-border pb-2">
        <input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') void run(value);
          }}
          placeholder="When did we buy the TV?"
          className="h-12 min-w-0 flex-1 bg-transparent text-[17px] outline-none"
          data-testid="input-ask-verid"
        />
        <button type="button" onClick={() => void run(value)} className="text-sm font-semibold">
          Ask
        </button>
      </div>
      <div className="mt-5 flex flex-wrap gap-2">
        {prompts.map((prompt) => (
          <button key={prompt} type="button" onClick={() => void run(prompt)} className="rounded-full border border-border px-3 py-1.5 text-[12px] text-muted-foreground">
            {prompt}
          </button>
        ))}
      </div>
      <div className="mt-10 min-h-[8rem]">
        {busy && <p className="text-sm text-muted-foreground">Reading the household graph…</p>}
        {!busy && reply && (
          <div>
            <p className="text-[17px] leading-relaxed">{reply.answer}</p>
            {reply.why && <p className="mt-4 text-sm text-muted-foreground">{reply.why}</p>}
            <div className="mt-4 flex flex-wrap gap-2">
              {(reply.sources || []).map((source) => (
                source.passportId ? (
                  <Link key={`${source.passportId}-${source.field}`} href={`/memory/${source.passportId}`} className="text-[12px] text-muted-foreground underline">
                    {source.passportId} · {source.field}
                  </Link>
                ) : null
              ))}
            </div>
            <p className="mt-6 text-[12px] text-muted-foreground">
              {reply.engine === 'gemma' ? 'Gemma 2 phrased this from vault fields.' : 'Answered from stored records. Unknown stays unknown.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export function PrivacyPage() {
  return (
    <div className="page-enter max-w-[56ch]">
      <p className="font-mono-ui text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Privacy</p>
      <h1 className="mt-3 font-display text-3xl font-semibold tracking-[-0.04em]">What stays here</h1>
      <div className="mt-8 space-y-6 text-[15px] leading-relaxed text-muted-foreground">
        <p>Invoices, serials, and photos are written to a local vault on this machine (`household-vault.json`). They are not uploaded to a Verid cloud.</p>
        <p>OCR (RapidOCR) and appliance detection (YOLO) run in the local Python engine.</p>
        <p>Qwen2.5-VL and Gemma 2 run only if Ollama is running on this computer. If they are off, Verid still answers from the vault with deterministic lookup.</p>
        <p>We do not claim airplane-mode isolation when the phone is talking to a laptop on your LAN. That laptop is still your machine — not a public API.</p>
      </div>
    </div>
  );
}

export function CameraHint({ node }: { node: GraphNode | null }) {
  if (!node) return null;
  return (
    <div className="mt-4 rounded-2xl border border-border p-4">
      <div className="text-[11px] uppercase tracking-[0.14em] text-muted-foreground">Remembered</div>
      <div className="mt-1 text-lg font-semibold">{node.passport.product}</div>
      <p className="mt-1 text-sm text-muted-foreground">
        {daysLabel(node.warrantyDaysLeft)}
        {node.room ? ` · ${node.room.name}` : ''}
        {node.memory.locationNote ? ` — ${node.memory.locationNote}` : ''}
      </p>
      <div className="mt-3 flex gap-2 text-sm">
        <Link href={`/memory/${node.passport.passportId}`} className="underline">Details</Link>
        <Link href="/ask" className="underline">Ask</Link>
        <span className="inline-flex items-center gap-1 text-muted-foreground"><MapPin size={12} /> {node.memory.lastSeenConfidence}</span>
        {node.passport.sourceDocument && <span className="inline-flex items-center gap-1 text-muted-foreground"><FileText size={12} /> Invoice</span>}
        <span className="inline-flex items-center gap-1 text-muted-foreground"><Camera size={12} /> {node.passport.physicalProductImage ? 'Photo' : 'No photo'}</span>
      </div>
    </div>
  );
}
