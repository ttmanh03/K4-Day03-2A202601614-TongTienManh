import type { TraceStep } from "../types";

const STEP_STYLE: Record<
  TraceStep["type"],
  { icon: string; label: string; accent: string; bg: string }
> = {
  plan: { icon: "checklist", label: "Planning", accent: "text-secondary", bg: "bg-secondary-container/25" },
  thought: { icon: "psychology", label: "Thought", accent: "text-secondary", bg: "bg-secondary-container/20" },
  action: { icon: "bolt", label: "Action", accent: "text-primary", bg: "bg-primary-container/10" },
  observation: { icon: "visibility", label: "Observation", accent: "text-on-surface-variant", bg: "bg-surface-container-low" },
  memory: { icon: "database", label: "Memory", accent: "text-tertiary", bg: "bg-tertiary-fixed/50" },
  evaluation: { icon: "fact_check", label: "Self-Evaluation", accent: "text-secondary", bg: "bg-secondary-fixed/50" },
  final: { icon: "flag", label: "Final Answer", accent: "text-primary", bg: "bg-primary-container/15" },
  guardrail: { icon: "shield", label: "Guardrail", accent: "text-error", bg: "bg-error-container/40" },
  error: { icon: "error", label: "Lỗi", accent: "text-error", bg: "bg-error-container/40" },
};

export default function TraceStepCard({ step, isLast }: { step: TraceStep; isLast: boolean }) {
  const style = STEP_STYLE[step.type];

  return (
    <div className="flex gap-3 relative pl-1">
      {!isLast && <div className="absolute left-[19px] top-9 bottom-0 w-px bg-surface-variant" />}
      <div
        className={`shrink-0 w-9 h-9 rounded-full flex items-center justify-center ${style.bg} ${style.accent}`}
      >
        <span className="material-symbols-outlined text-[18px]">{style.icon}</span>
      </div>
      <div className={`flex-1 rounded-lg px-4 py-3 ${style.bg} mb-4`}>
        <div className={`text-label-sm font-label-sm uppercase tracking-wide mb-1 ${style.accent}`}>
          {style.label} · bước {step.step}
        </div>
        {step.type === "action" ? (
          <code className="text-body-md font-mono text-on-surface break-words">
            {step.tool}({JSON.stringify(step.args)})
          </code>
        ) : (
          <p className="text-body-md font-body-md text-on-surface leading-relaxed whitespace-pre-line">
            {step.content}
          </p>
        )}
      </div>
    </div>
  );
}
