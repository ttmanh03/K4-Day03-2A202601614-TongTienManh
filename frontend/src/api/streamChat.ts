import type { TestCase, TraceStep } from "../types";

const API_BASE = "/api";

export async function fetchBaseline(query: string): Promise<string> {
  const res = await fetch(`${API_BASE}/chat/baseline`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    throw new Error(`Baseline request failed: ${res.status}`);
  }
  const data = await res.json();
  return data.response as string;
}

/**
 * POST /api/chat/react trả về SSE (Content-Type: text/event-stream).
 * EventSource native chỉ hỗ trợ GET nên tự đọc ReadableStream + tách frame "data: ...\n\n".
 */
export async function streamReact(
  query: string,
  onStep: (step: TraceStep) => void,
): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/react`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok || !res.body) {
    throw new Error(`ReAct request failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sepIndex: number;
    while ((sepIndex = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, sepIndex).trim();
      buffer = buffer.slice(sepIndex + 2);
      if (!rawEvent.startsWith("data:")) continue;

      const jsonStr = rawEvent.slice("data:".length).trim();
      if (!jsonStr) continue;
      try {
        onStep(JSON.parse(jsonStr) as TraceStep);
      } catch (err) {
        console.error("Không parse được SSE event:", err, jsonStr);
      }
    }
  }
}

export async function fetchTestCases(): Promise<TestCase[]> {
  const res = await fetch(`${API_BASE}/test-cases`);
  if (!res.ok) throw new Error(`Test-cases request failed: ${res.status}`);
  return res.json();
}
