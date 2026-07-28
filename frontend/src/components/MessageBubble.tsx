import { LEVELS, type ChatMessage } from "../types";

interface Props {
  message: ChatMessage;
  onOpenTrace: (message: ChatMessage) => void;
}

export default function MessageBubble({ message, onOpenTrace }: Props) {
  const meta = LEVELS.find((l) => l.level === message.level)!;

  if (message.role === "user") {
    return (
      <div className="flex flex-col items-end gap-2 w-full">
        <div className="flex items-center gap-3 mr-2 text-label-sm font-label-sm text-on-surface-variant">
          Bạn
        </div>
        <div className="max-w-[80%] bg-surface-container-high rounded-t-2xl rounded-bl-2xl rounded-br-sm px-6 py-4 shadow-sm text-body-md font-body-md text-on-surface">
          {message.content}
        </div>
      </div>
    );
  }

  const stepCount = message.trace?.length ?? 0;
  const toolCalls = message.trace?.filter((s) => s.type === "action").length ?? 0;

  return (
    <div className="flex flex-col items-start gap-2 w-full">
      <div className="flex items-center gap-3 ml-2">
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shadow-[0_4px_12px_rgba(182,14,61,0.25)]">
          <span
            className="material-symbols-outlined text-[16px] text-on-primary"
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            {meta.icon}
          </span>
        </div>
        <span className="text-label-sm font-label-sm text-primary tracking-wide uppercase">
          {meta.short} · {meta.name}
        </span>
      </div>

      <div className="max-w-[85%] bg-surface-container-lowest rounded-t-2xl rounded-br-2xl rounded-bl-sm px-6 py-5 shadow-[0_4px_24px_rgba(132,51,196,0.06)] ring-1 ring-surface-variant/20 relative">
        <div className="absolute -left-1 top-4 w-2 h-6 bg-primary rounded-r-md" />

        {message.content ? (
          <p className="text-body-md font-body-md text-on-surface leading-relaxed whitespace-pre-line">
            {message.content}
          </p>
        ) : (
          <p className="text-body-md font-body-md text-on-surface-variant italic animate-pulse">
            {meta.level === 4 ? "Đang lập kế hoạch..." : "Đang suy nghĩ..."}
          </p>
        )}

        {meta.streaming && stepCount > 0 && (
          <button
            onClick={() => onOpenTrace(message)}
            className="mt-4 flex items-center gap-2 bg-gradient-to-br from-surface-container-low to-surface-bright rounded-xl px-4 py-3 border border-outline-variant/30 shadow-sm hover:shadow-[0_8px_20px_rgba(182,14,61,0.08)] hover:-translate-y-0.5 transition-all w-full text-left"
          >
            <span className="material-symbols-outlined text-primary text-[18px]">psychology</span>
            <span className="text-label-md font-label-md text-on-surface flex-1">
              {stepCount} bước · {toolCalls} lần gọi tool
              {message.isStreaming ? " · đang chạy..." : ""}
            </span>
            <span className="text-label-sm font-label-sm text-primary whitespace-nowrap">
              Xem suy luận →
            </span>
          </button>
        )}

        {!meta.streaming && !message.isStreaming && (
          <p className="mt-3 text-label-sm font-label-sm text-on-surface-variant/70 italic">
            {meta.level === 1
              ? "Cấp 1 không có suy luận — chỉ khớp từ khóa cố định."
              : "Cấp 2 không gọi tool nên không có trace suy luận."}
          </p>
        )}
      </div>
    </div>
  );
}
