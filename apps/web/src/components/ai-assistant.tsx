import { useEffect, useRef, useState, type KeyboardEvent } from 'react';
import { useLocation } from 'wouter';
import { BrainCircuit, Mic, Send, ShieldCheck, Sparkles, X, Zap } from 'lucide-react';
import { askHousehold, type HouseholdAskResult } from '@/lib/household';

const QUICK_PROMPTS = [
  { icon: ShieldCheck, label: 'What needs my attention?', hint: 'attention' },
  { icon: Zap, label: 'Where is my AC warranty?', hint: 'warranty' },
  { icon: BrainCircuit, label: 'Prepare a claim pack', hint: 'claim' },
];

type ChatMessage = { role: 'assistant' | 'user'; text: string; meta?: HouseholdAskResult };

export function AiAssistant() {
  const [, setLocation] = useLocation();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      text: 'Hovira answers from your local passport vault. Gemma 2 paraphrases when Ollama is running; otherwise I use deterministic field lookup. I will not invent serials.',
    },
  ]);
  const [input, setInput] = useState('');
  const [thinking, setThinking] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const listening = useRef(false);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, thinking, open]);

  const applyIntent = (result: HouseholdAskResult) => {
    if (result.intent === 'claim_pack' && result.passportId) {
      setLocation(`/passports/${result.passportId}?claim=1`);
    } else if ((result.intent === 'open_passport' || result.intent === 'warranty') && result.passportId) {
      setLocation(`/passports/${result.passportId}`);
    }
  };

  const send = async (text: string) => {
    const value = text.trim();
    if (!value || thinking) return;
    setMessages((prev) => [...prev, { role: 'user', text: value }]);
    setInput('');
    setThinking(true);
    try {
      const result = await askHousehold(value);
      const engine = result.gemmaModel || result.engine || 'vault';
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: result.answer,
          meta: result,
        },
        ...(result.why
          ? [{ role: 'assistant' as const, text: `Why: ${result.why} · ${engine}` }]
          : []),
      ]);
      applyIntent(result);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'The household engine is offline. Start the AI service (port 8000) and retry.' },
      ]);
    } finally {
      setThinking(false);
    }
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') void send(input);
  };

  const startVoice = () => {
    const SpeechRecognition = (window as unknown as { webkitSpeechRecognition?: new () => SpeechRecognition }).webkitSpeechRecognition
      || (window as unknown as { SpeechRecognition?: new () => SpeechRecognition }).SpeechRecognition;
    if (!SpeechRecognition) return;
    if (listening.current) return;
    const rec = new SpeechRecognition();
    rec.lang = 'en-IN';
    rec.onresult = (event: SpeechRecognitionEvent) => {
      const said = event.results[0]?.[0]?.transcript;
      if (said) void send(said);
    };
    rec.onend = () => {
      listening.current = false;
    };
    listening.current = true;
    rec.start();
  };

  return (
    <>
      <button
        onClick={() => setOpen((value) => !value)}
        className={`ai-fab fixed right-4 z-50 flex h-14 w-14 items-center justify-center rounded-full text-white bottom-[calc(6.2rem_+_env(safe-area-inset-bottom,0px))] lg:bottom-6 ${open ? 'ai-fab-open' : ''}`}
        aria-label={open ? 'Close AI assistant' : 'Open AI assistant'}
        aria-expanded={open}
        data-testid="button-ai-assistant"
      >
        {open ? <X size={22} /> : (
          <span className="relative flex h-7 w-7 items-center justify-center overflow-hidden rounded-full ai-orb" style={{ background: '#2a2e33' }}>
            <Sparkles size={15} className="relative z-10 text-[#dfe4e9]" strokeWidth={2.2} />
          </span>
        )}
      </button>

      {open && (
        <div className="ai-chat fixed right-4 z-50 h-[min(540px,calc(100dvh-12.5rem))] w-[min(400px,calc(100vw-2rem))] bottom-[calc(11rem_+_env(safe-area-inset-bottom,0px))] lg:bottom-24 lg:h-[min(600px,calc(100dvh-7rem))]" data-testid="panel-ai-assistant">
          <div className="ai-chat-inner">
            <div className="flex items-center gap-3 border-b border-white/10 px-5 py-4">
              <div className="ai-orb relative flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl" style={{ background: '#2e3238' }}>
                <Sparkles size={18} className="relative z-10 text-[#e6eaee]" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-sm font-semibold text-[#e8e8e8]">Hovira Assistant</div>
                <div className="mt-0.5 text-[11px] text-[#a2a7ad]">Grounded vault · Gemma 2 when local</div>
              </div>
              <button onClick={() => setOpen(false)} className="rounded-lg p-1.5 text-[#a2a7ad] transition hover:bg-white/10 hover:text-white" aria-label="Close assistant"><X size={16} /></button>
            </div>

            <div ref={scrollRef} className="ai-chat-inner flex-1 gap-3 overflow-y-auto px-4 py-4">
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-[13px] leading-relaxed ${message.role === 'user' ? 'ai-msg-user text-[#e8e8e8]' : 'ai-msg-assistant text-[#cfd4d9]'}`}>
                    {message.role === 'assistant' && (
                      <div className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[.14em] text-[#8a9198]">
                        <BrainCircuit size={11} /> Hovira
                      </div>
                    )}
                    {message.text}
                    {message.meta?.sources?.length ? (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {message.meta.sources.map((source) => (
                          <span key={`${source.passportId}-${source.field}`} className="rounded-full border border-white/10 px-2 py-0.5 text-[10px] text-[#9aa1a8]">
                            {source.passportId} · {source.field}
                          </span>
                        ))}
                      </div>
                    ) : null}
                  </div>
                </div>
              ))}
              {thinking && (
                <div className="flex justify-start">
                  <div className="ai-msg-assistant typing-dots flex items-center gap-1 rounded-2xl px-3.5 py-3">
                    <span /><span /><span />
                  </div>
                </div>
              )}
            </div>

            <div className="border-t border-white/10 px-4 py-3">
              <div className="mb-2.5 flex gap-2 overflow-x-auto pb-0.5">
                {QUICK_PROMPTS.map((prompt) => {
                  const Icon = prompt.icon;
                  return (
                    <button key={prompt.label} onClick={() => void send(prompt.label)} className="ai-chip shrink-0" data-testid={`button-ai-prompt-${prompt.hint}`}>
                      <Icon size={12} /> {prompt.label}
                    </button>
                  );
                })}
              </div>
              <div className="flex items-center gap-2 rounded-2xl border border-white/12 bg-white/[0.05] p-1.5 pl-3.5">
                <button type="button" onClick={startVoice} aria-label="Voice ask" className="shrink-0 text-[#8a9198] hover:text-white">
                  <Mic size={15} />
                </button>
                <input
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={onKeyDown}
                  placeholder="Ask from your passports…"
                  className="h-9 min-w-0 flex-1 bg-transparent text-[13px] text-[#e8e8e8] outline-none placeholder:text-[#70757c]"
                  data-testid="input-ai-prompt"
                />
                <button
                  onClick={() => void send(input)}
                  disabled={!input.trim() || thinking}
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-[#c8cdd2] text-[#121212] disabled:opacity-40"
                  aria-label="Send prompt"
                >
                  <Send size={14} />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

interface SpeechRecognition extends EventTarget {
  lang: string;
  start: () => void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onend: (() => void) | null;
}

interface SpeechRecognitionEvent {
  results: ArrayLike<ArrayLike<{ transcript: string }>>;
}
