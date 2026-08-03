import { Lightbulb, RefreshCw } from "lucide-react";
import Button from "./Button.jsx";

// Panel with the recommendation returned by the backend and a button to
// start a new diagnosis.
function RecommendationCard({ recommendation, personalized, onRestart }) {
  return (
    <div className="rounded-2xl bg-itaca-panel p-6 shadow-card sm:p-7">
      <div className="flex flex-wrap items-center gap-2.5">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-itaca-blue/20 text-itaca-blue">
          <Lightbulb className="h-5 w-5" />
        </span>
        <h3 className="text-[18px] font-bold text-itaca-text">Recomendación</h3>
        {personalized && (
          <span className="rounded-full bg-itaca-gold/20 px-3 py-1 text-[12px] font-semibold text-itaca-gold">
            Personalizada
          </span>
        )}
      </div>

      {/* Gold border marks the model-driven output; the fill stays dark so
          the accent never becomes a large surface. */}
      <div className="mt-4 rounded-xl border-2 border-itaca-gold bg-itaca-gold/5 p-5">
        <p className="text-[17px] font-bold leading-relaxed text-itaca-text sm:text-[19px]">
          {recommendation}
        </p>
      </div>

      <div className="mt-6">
        <Button
          variant="outline"
          icon={RefreshCw}
          onClick={onRestart}
          className="w-full sm:w-auto"
        >
          Realizar otro diagnóstico
        </Button>
      </div>
    </div>
  );
}

export default RecommendationCard;
