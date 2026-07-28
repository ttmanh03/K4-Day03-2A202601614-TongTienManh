interface Props {
  open: boolean;
  facts: Record<string, string>;
  turnCount: number;
  onClose: () => void;
  onClear: () => void;
}

export default function MemoryPanel({ open, facts, turnCount, onClose, onClear }: Props) {
  const entries = Object.entries(facts);

  return (
    <aside
      className={`fixed top-0 right-0 h-full w-full sm:w-[380px] bg-surface-container-lowest border-l border-surface-variant/30 shadow-[-8px_0_32px_rgba(0,0,0,0.06)] z-40 transition-transform duration-500 ease-[cubic-bezier(0.2,0.8,0.2,1)] ${
        open ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="flex items-center justify-between px-6 py-5 border-b border-surface-variant/40 sticky top-0 bg-surface-container-lowest/80 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-secondary text-[20px]">database</span>
          <h2 className="text-headline-md font-headline-md text-on-surface" style={{ fontSize: 18 }}>
            Bộ nhớ
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

      <div className="px-6 py-6 overflow-y-auto h-[calc(100%-140px)] flex flex-col gap-6">
        <section>
          <h3 className="text-label-md font-label-md text-secondary uppercase tracking-wide mb-3">
            Long-term · {entries.length} thông tin
          </h3>
          {entries.length ? (
            <ul className="flex flex-col gap-2">
              {entries.map(([k, v]) => (
                <li key={k} className="bg-secondary-fixed/40 rounded-lg px-4 py-3">
                  <div className="text-label-sm font-label-sm text-on-secondary-fixed-variant uppercase tracking-wide">
                    {k}
                  </div>
                  <div className="text-body-md font-body-md text-on-surface">{v}</div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-body-md font-body-md text-on-surface-variant">
              Chưa ghi nhớ gì. Thử nói "Mình là INTJ, sống ở Hà Nội" rồi hỏi tiếp ở lượt sau.
            </p>
          )}
        </section>

        <section>
          <h3 className="text-label-md font-label-md text-tertiary uppercase tracking-wide mb-3">
            Short-term · {turnCount}/5 lượt gần nhất
          </h3>
          <p className="text-body-md font-body-md text-on-surface-variant">
            5 lượt hội thoại gần nhất được nạp làm ngữ cảnh cho Cấp 2, 3 và 4.
          </p>
        </section>
      </div>

      <div className="absolute bottom-0 left-0 right-0 px-6 py-4 border-t border-surface-variant/40 bg-surface-container-lowest">
        <button
          onClick={onClear}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-full bg-error-container text-on-error-container text-label-md font-label-md hover:opacity-90 transition-opacity"
        >
          <span className="material-symbols-outlined text-[18px]">delete</span>
          Xóa toàn bộ bộ nhớ
        </button>
      </div>
    </aside>
  );
}
