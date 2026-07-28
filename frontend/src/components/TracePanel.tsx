import type { ChatMessage } from "../types";
import TraceStepCard from "./TraceStepCard";

interface Props {
  message: ChatMessage | null;
  onClose: () => void;
}

export default function TracePanel({ message, onClose }: Props) {
  const isOpen = message !== null;

  return (
    <aside
      className={`fixed top-0 right-0 h-full w-full sm:w-[420px] bg-surface-container-lowest border-l border-surface-variant/30 shadow-[-8px_0_32px_rgba(0,0,0,0.06)] z-30 transition-transform duration-500 ease-[cubic-bezier(0.2,0.8,0.2,1)] ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="flex items-center justify-between px-6 py-5 border-b border-surface-variant/40 bg-surface-container-lowest/80 backdrop-blur-md sticky top-0">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[20px]">psychology</span>
          <h2 className="text-headline-md font-headline-md text-on-surface" style={{ fontSize: 18 }}>
            Luồng Suy luận
          </h2>
        </div>
        <button
          onClick={onClose}
          className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-surface-container-high transition-colors"
          aria-label="Đóng"
        >
          <span className="material-symbols-outlined text-on-surface-variant text-[20px]">close</span>
        </button>
      </div>

      <div className="px-6 py-6 overflow-y-auto h-[calc(100%-77px)]">
        {message?.trace && message.trace.length > 0 ? (
          <div className="flex flex-col">
            {message.trace.map((step, i) => (
              <TraceStepCard key={i} step={step} isLast={i === message.trace!.length - 1} />
            ))}
            {message.isStreaming && (
              <div className="flex items-center gap-2 text-on-surface-variant text-label-sm font-label-sm pl-1 animate-pulse">
                <span className="material-symbols-outlined text-[18px]">more_horiz</span>
                Đang suy luận thêm...
              </div>
            )}
          </div>
        ) : (
          <p className="text-body-md font-body-md text-on-surface-variant">
            Chưa có bước suy luận nào để hiển thị.
          </p>
        )}
      </div>
    </aside>
  );
}
