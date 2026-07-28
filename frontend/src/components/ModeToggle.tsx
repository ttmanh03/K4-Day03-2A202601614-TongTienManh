import type { Mode } from "../types";

interface Props {
  mode: Mode;
  onChange: (mode: Mode) => void;
  disabled?: boolean;
}

const OPTIONS: { value: Mode; label: string; icon: string }[] = [
  { value: "baseline", label: "Chatbot Baseline", icon: "chat_bubble" },
  { value: "agent", label: "ReAct Agent", icon: "psychology" },
];

export default function ModeToggle({ mode, onChange, disabled }: Props) {
  return (
    <div className="inline-flex bg-surface-container p-1 rounded-full gap-1">
      {OPTIONS.map((opt) => {
        const active = mode === opt.value;
        return (
          <button
            key={opt.value}
            onClick={() => onChange(opt.value)}
            disabled={disabled}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-label-md font-label-md transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
              active
                ? "bg-primary text-on-primary shadow-[0_4px_12px_rgba(182,14,61,0.25)]"
                : "text-on-surface-variant hover:bg-surface-container-high"
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">{opt.icon}</span>
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}
