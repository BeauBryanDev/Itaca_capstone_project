import { Database, FileSearch, LineChart } from "lucide-react";

const stages = [
  { id: 0, label: "Recopilando datos", icon: Database, color: "#B50F19" },
  { id: 1, label: "Procesando información", icon: FileSearch, color: "#1393B2" },
  { id: 2, label: "Generando resultados", icon: LineChart, color: "#998000" },
];

// Circular loader + progress bar + percentage + processing stages.
// progress: number from 0 to 100.
function ProgressLoader({ progress = 0 }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;

  // Which stage is active depends on progress thresholds.
  const activeStage = progress < 40 ? 0 : progress < 80 ? 1 : 2;

  return (
    <div className="flex flex-col items-center">
      {/* Circular loader */}
      <div className="relative h-36 w-36">
        <svg className="h-full w-full -rotate-90" viewBox="0 0 130 130">
          <circle
            cx="65"
            cy="65"
            r={radius}
            fill="none"
            stroke="#2f3335"
            strokeWidth="10"
          />
          <circle
            cx="65"
            cy="65"
            r={radius}
            fill="none"
            stroke="url(#loaderGradient)"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.3s ease" }}
          />
          <defs>
            <linearGradient id="loaderGradient" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#1393B2" />
              <stop offset="100%" stopColor="#B50F19" />
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <LineChart className="h-11 w-11 text-itaca-subtext" />
        </div>
      </div>

      <h2 className="mt-6 text-center text-[24px] font-bold text-itaca-text">
        Analizando tu diagnóstico...
      </h2>
      <p className="mt-2 max-w-md text-center text-[15px] leading-relaxed text-itaca-subtext">
        Nuestro modelo está evaluando la información de tu empresa para generar
        los mejores insights.
      </p>

      {/* Progress bar */}
      <div className="mt-7 flex w-full max-w-md items-center gap-4">
        <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-[#2f3335]">
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{
              width: `${progress}%`,
              background: "linear-gradient(90deg, #1393B2, #B50F19)",
            }}
          />
        </div>
        <span className="w-12 text-right text-[22px] font-bold text-itaca-text">
          {Math.round(progress)}%
        </span>
      </div>

      {/* Processing stages */}
      <div className="mt-9 flex w-full max-w-lg items-start justify-between">
        {stages.map((stage, index) => {
          const isActive = index <= activeStage;
          return (
            <div key={stage.id} className="relative flex flex-1 flex-col items-center">
              {index < stages.length - 1 && (
                <span className="absolute left-1/2 top-7 hidden h-px w-full border-t border-dashed border-white/20 sm:block" />
              )}
              <div
                className="z-10 flex h-14 w-14 items-center justify-center rounded-full border-2 bg-itaca-bg transition-colors"
                style={{
                  borderColor: isActive ? stage.color : "#3a3d3f",
                  color: isActive ? stage.color : "#6b6f71",
                }}
              >
                <stage.icon className="h-6 w-6" />
              </div>
              <span
                className={
                  "mt-2 max-w-[90px] text-center text-[13px] " +
                  (isActive ? "text-itaca-text" : "text-gray-500")
                }
              >
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ProgressLoader;
