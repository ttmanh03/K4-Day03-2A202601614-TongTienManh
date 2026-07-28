import { useEffect, useRef, useState } from "react";
import { fetchBaseline, fetchTestCases, streamReact } from "./api/streamChat";
import ChatWindow from "./components/ChatWindow";
import ModeToggle from "./components/ModeToggle";
import TracePanel from "./components/TracePanel";
import type { ChatMessage, Mode, TestCase, TraceStep } from "./types";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [mode, setMode] = useState<Mode>("agent");
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [openTraceId, setOpenTraceId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

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
      mode,
      content: query,
    };
    const botId = crypto.randomUUID();
    const botMsg: ChatMessage = {
      id: botId,
      role: "assistant",
      mode,
      content: "",
      trace: mode === "agent" ? [] : undefined,
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMsg, botMsg]);
    setInput("");
    setBusy(true);

    try {
      if (mode === "baseline") {
        const answer = await fetchBaseline(query);
        patchMessage(botId, { content: answer, isStreaming: false });
      } else {
        setOpenTraceId(botId);
        await streamReact(query, (step) => {
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
      <header className="flex items-center justify-between px-6 sm:px-10 py-4 border-b border-surface-variant/40 bg-surface-container-lowest/70 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#FF4D6D] to-[#9D4EDD] flex items-center justify-center">
            <span
              className="material-symbols-outlined text-[18px] text-white"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              favorite
            </span>
          </div>
          <span className="text-headline-md font-headline-md text-primary" style={{ fontSize: 20 }}>
            Cupid Agent
          </span>
        </div>
        <ModeToggle mode={mode} onChange={setMode} disabled={busy} />
      </header>

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
            placeholder={
              mode === "agent" ? "Hỏi Cupid Agent bất cứ điều gì..." : "Hỏi Chatbot Baseline..."
            }
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
