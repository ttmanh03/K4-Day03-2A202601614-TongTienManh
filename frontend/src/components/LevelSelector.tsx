import { LEVELS, type Level } from "../types";

interface Props {
  level: Level;
  onChange: (level: Level) => void;
  disabled?: boolean;
}

export default function LevelSelector({ level, onChange, disabled }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {LEVELS.map((meta) => {
        const active = meta.level === level;
        return (
          <button
            key={meta.level}
            onClick={() => onChange(meta.level)}
            disabled={disabled}
            title={meta.desc}
            className={`flex items-center gap-2 px-3 py-2 rounded-full text-label-md font-label-md transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
              active
                ? "bg-primary text-on-primary shadow-[0_4px_12px_rgba(182,14,61,0.25)]"
                : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high"
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">{meta.icon}</span>
            <span className="hidden sm:inline">
              {meta.short}: {meta.name}
            </span>
            <span className="sm:hidden">{meta.short}</span>
          </button>
        );
      })}
    </div>
  );
}
