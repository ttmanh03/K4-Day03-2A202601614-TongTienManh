import { useEffect, useRef } from "react";
import type { ChatMessage, TestCase } from "../types";
import MessageBubble from "./MessageBubble";

interface Props {
  messages: ChatMessage[];
  testCases: TestCase[];
  onOpenTrace: (message: ChatMessage) => void;
  onPickSuggestion: (question: string) => void;
}

export default function ChatWindow({ messages, testCases, onOpenTrace, onPickSuggestion }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        <div className="w-28 h-28 rounded-full bg-primary-fixed/50 flex items-center justify-center mb-8">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#FF4D6D] to-[#9D4EDD] flex items-center justify-center">
            <span
              className="material-symbols-outlined text-[36px] text-white"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              favorite
            </span>
          </div>
        </div>

        <h1 className="text-headline-lg font-headline-lg text-on-surface text-center">Tìm đúng người.</h1>
        <h1 className="text-headline-lg font-headline-lg text-center bg-gradient-to-r from-[#FF4D6D] to-[#9D4EDD] bg-clip-text text-transparent mb-4">
          Hiểu đúng nhau.
        </h1>
        <p className="text-body-md font-body-md text-on-surface-variant text-center max-w-lg mb-10">
          Chọn 1 trong 4 cấp độ AI ở thanh trên, rồi đặt cùng một câu hỏi để thấy rõ sự khác biệt:
          từ bot khớp từ khóa cố định đến agent tự lập kế hoạch và gọi công cụ.
        </p>

        <div className="grid sm:grid-cols-2 gap-3 w-full max-w-3xl">
          {testCases.slice(0, 4).map((tc) => (
            <button
              key={tc.id}
              onClick={() => onPickSuggestion(tc.question)}
              className="flex items-start gap-3 bg-surface-container-low hover:bg-surface-container rounded-xl px-4 py-4 text-left transition-colors"
            >
              <span className="material-symbols-outlined text-secondary text-[20px] shrink-0">
                auto_awesome
              </span>
              <span className="text-body-md font-body-md text-on-surface line-clamp-2">
                {tc.question}
              </span>
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-6 py-8">
      <div className="max-w-3xl mx-auto flex flex-col gap-8">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} onOpenTrace={onOpenTrace} />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
