import { useEffect, useRef, useState } from "react";
import { fetchPlain, fetchTestCases, streamSteps } from "./api/streamChat";
import ChatWindow from "./components/ChatWindow";
import LevelSelector from "./components/LevelSelector";
import TracePanel from "./components/TracePanel";
import { LEVELS, type ChatMessage, type Level, type TestCase, type TraceStep } from "./types";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [level, setLevel] = useState<Level>(3);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [openTraceId, setOpenTraceId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const meta = LEVELS.find((l) => l.level === level)!;

  useEffect(() => {
    fetchTestCases().then(setTestCases).catch(console.error);
  }, []);

  const patchMessage = (id: string, patch: Partial<ChatMessage>) => {
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, ...patch } : m)));
  };

  const appendTraceStep = (id: string, step: TraceStep) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? { ...m, trace: [...(m.trace ?? []), step] } : m)),
    );
  };

  const send = async (question: string) => {
    const query = question.trim();
    if (!query || busy) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      level,
      content: query,
    };
    const botId = crypto.randomUUID();
    const botMsg: ChatMessage = {
      id: botId,
      role: "assistant",
      level,
      content: "",
      trace: meta.streaming ? [] : undefined,
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMsg, botMsg]);
    setInput("");
    setBusy(true);

    try {
      if (!meta.streaming) {
        const answer = await fetchPlain(meta.endpoint, query);
        patchMessage(botId, { content: answer, isStreaming: false });
      } else {
        setOpenTraceId(botId);
        await streamSteps(meta.endpoint, query, (step) => {
          appendTraceStep(botId, step);
          if (step.type === "final" || step.type === "guardrail" || step.type === "error") {
            patchMessage(botId, { content: step.content });
          }
        });
        patchMessage(botId, { isStreaming: false });
      }
    } catch (err) {
      patchMessage(botId, {
        content: `Lỗi khi gọi backend: ${err instanceof Error ? err.message : String(err)}`,
        isStreaming: false,
      });
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  };

  const openTraceMessage = messages.find((m) => m.id === openTraceId) ?? null;

  return (
    <div className="h-screen flex flex-col bg-background">
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-6 sm:px-10 py-4 border-b border-surface-variant/40 bg-surface-container-lowest/70 backdrop-blur-md">
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#FF4D6D] to-[#9D4EDD] flex items-center justify-center">
            <span
              className="material-symbols-outlined text-[18px] text-white"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              favorite
            </span>
          </div>
          <div>
            <div className="text-headline-md font-headline-md text-primary" style={{ fontSize: 20 }}>
              Cupid Agent
            </div>
            <div className="text-label-sm font-label-sm text-on-surface-variant">
              4 cấp độ AI hội thoại
            </div>
          </div>
        </div>
        <LevelSelector level={level} onChange={setLevel} disabled={busy} />
      </header>

      <div className="px-6 sm:px-10 py-2 bg-surface-container-low border-b border-surface-variant/30">
        <p className="text-label-sm font-label-sm text-on-surface-variant text-center">
          <span className="text-primary font-semibold">
            {meta.short} — {meta.name}:
          </span>{" "}
          {meta.desc}
        </p>
      </div>

      <ChatWindow
        messages={messages}
        testCases={testCases}
        onOpenTrace={(m) => setOpenTraceId(m.id)}
        onPickSuggestion={send}
      />

      <div className="px-6 sm:px-10 py-5 border-t border-surface-variant/40 bg-surface-container-lowest/70 backdrop-blur-md">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="max-w-3xl mx-auto flex items-center gap-3 bg-surface-container-lowest rounded-full pl-6 pr-2 py-2 shadow-[0_4px_20px_rgba(0,0,0,0.04)] ring-1 ring-surface-variant/30 focus-within:ring-primary transition-shadow"
        >
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={busy}
            placeholder={`Hỏi ${meta.name} bất cứ điều gì...`}
            className="flex-1 bg-transparent outline-none text-body-md font-body-md text-on-surface placeholder:text-on-surface-variant/60 disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={busy || !input.trim()}
            className="w-10 h-10 rounded-full bg-primary text-on-primary flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed hover:bg-primary-container transition-colors"
            aria-label="Gửi"
          >
            <span className="material-symbols-outlined text-[20px]">
              {busy ? "hourglass_top" : "send"}
            </span>
          </button>
        </form>
        <p className="text-label-sm font-label-sm text-on-surface-variant/70 text-center mt-3">
          Cupid Agent đưa ra phân tích dựa trên tool giả lập. Hãy kiểm chứng thông tin quan trọng.
        </p>
      </div>

      <TracePanel message={openTraceMessage} onClose={() => setOpenTraceId(null)} />
    </div>
  );
}
