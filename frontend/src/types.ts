export type Level = 1 | 2 | 3 | 4;

export interface LevelMeta {
  level: Level;
  name: string;
  short: string;
  icon: string;
  desc: string;
  streaming: boolean;
  endpoint: string;
}

export const LEVELS: LevelMeta[] = [
  {
    level: 1,
    name: "Rule-Based Bot",
    short: "Cấp 1",
    icon: "rule",
    desc: "Khớp từ khóa if/else cố định, không có LLM",
    streaming: false,
    endpoint: "/api/chat/level1",
  },
  {
    level: 2,
    name: "LLM Chatbot",
    short: "Cấp 2",
    icon: "chat_bubble",
    desc: "Dùng LLM sinh text mượt, nhưng không gọi được Tool",
    streaming: false,
    endpoint: "/api/chat/baseline",
  },
  {
    level: 3,
    name: "Reactive Agent",
    short: "Cấp 3",
    icon: "psychology",
    desc: "Suy luận Thought → Action → Observation & gọi Tool",
    streaming: true,
    endpoint: "/api/chat/react",
  },
  {
    level: 4,
    name: "Autonomous Agent",
    short: "Cấp 4",
    icon: "rocket_launch",
    desc: "Tự rã mục tiêu (Planning), tự đánh giá & có Memory",
    streaming: true,
    endpoint: "/api/chat/autonomous",
  },
];

export type TraceStep =
  | { type: "plan"; step: number; content: string }
  | { type: "thought"; step: number; content: string }
  | { type: "action"; step: number; tool: string; args: Record<string, unknown> }
  | { type: "observation"; step: number; content: string }
  | { type: "memory"; step: number; content: string }
  | { type: "evaluation"; step: number; content: string }
  | { type: "final"; step: number; content: string }
  | { type: "guardrail"; step: number; content: string }
  | { type: "error"; step: number; content: string };

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  level: Level;
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
