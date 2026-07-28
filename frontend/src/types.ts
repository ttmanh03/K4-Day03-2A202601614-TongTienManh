export type Mode = "baseline" | "agent";

export type TraceStep =
  | { type: "thought"; step: number; content: string }
  | { type: "action"; step: number; tool: string; args: Record<string, unknown> }
  | { type: "observation"; step: number; content: string }
  | { type: "final"; step: number; content: string }
  | { type: "guardrail"; step: number; content: string }
  | { type: "error"; step: number; content: string };

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  mode: Mode;
  content: string;
  trace?: TraceStep[];
  isStreaming?: boolean;
}

export interface TestCase {
  id: number;
  category: string;
  question: string;
  expected_behavior: string;
}
