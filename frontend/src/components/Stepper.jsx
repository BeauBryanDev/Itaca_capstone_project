import { Check } from "lucide-react";

const steps = [
  { id: 1, label: "Información" },
  { id: 2, label: "Analizando" },
  { id: 3, label: "Resultados" },
];

// Three-step progress indicator (Información -> Analizando -> Resultados).
// current is the active step id (1, 2 or 3).
function Stepper({ current = 1 }) {
  return (
    <div className="flex items-start justify-between">
      {steps.map((step, index) => {
        const isActive = step.id === current;
        const isDone = step.id < current;
        return (
          <div key={step.id} className="flex flex-1 flex-col items-center">
            <div className="flex w-full items-center">
              {/* left connector */}
              <div
                className={
                  "h-0.5 flex-1 " +
                  (index === 0
                    ? "opacity-0"
                    : step.id <= current
                    ? "bg-itaca-blue"
                    : "bg-white/15")
                }
              />
              <div
                className={
                  "flex h-8 w-8 items-center justify-center rounded-full text-[13px] font-semibold transition-colors " +
                  (isActive
                    ? "bg-itaca-blue text-white"
                    : isDone
                    ? "bg-itaca-blue text-white"
                    : "border border-white/25 text-itaca-subtext")
                }
              >
                {isDone ? <Check className="h-4 w-4" /> : step.id}
              </div>
              {/* right connector */}
              <div
                className={
                  "h-0.5 flex-1 " +
                  (index === steps.length - 1
                    ? "opacity-0"
                    : step.id < current
                    ? "bg-itaca-blue"
                    : "bg-white/15")
                }
              />
            </div>
            <span
              className={
                "mt-2 text-[13px] " +
                (isActive ? "font-medium text-itaca-text" : "text-itaca-subtext")
              }
            >
              {step.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default Stepper;
