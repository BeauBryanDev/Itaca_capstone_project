import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ExternalLink } from "lucide-react";
import Button from "../components/Button.jsx";
import StatCard from "../components/StatCard.jsx";
import DoughnutChart from "../components/DoughnutChart.jsx";
import GaugeChart from "../components/GaugeChart.jsx";
import RecommendationCard from "../components/RecommendationCard.jsx";
import { useDiagnosis } from "../hooks/useDiagnosis.js";

// Third view: results dashboard with indicators, chart and recommendation.
function DashboardPage() {
  const navigate = useNavigate();
  const { results, recommendation, resetDiagnosis } = useDiagnosis();

  useEffect(() => {
    if (!results) navigate("/", { replace: true });
  }, [results, navigate]);

  if (!results) return null;

  function handleRestart() {
    resetDiagnosis();
    navigate("/", { replace: true });
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-10">
      <h1 className="text-[26px] font-bold text-itaca-text sm:text-[30px]">
        Resultados de tu diagnóstico
      </h1>
      <p className="mt-1 text-[15px] text-itaca-subtext">
        Así se encuentra tu empresa actualmente.
      </p>

      {/* Indicators */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="Nivel de Madurez"
          badge={results.maturityLevel}
          description={results.maturityDescription}
        />
        <StatCard
          label="Puntuación General"
          value={results.score}
          suffix="/100"
          description="Calculada a partir de la distribución de probabilidades del modelo."
        />
        <StatCard
          label="Confianza del Modelo"
          value={results.confidence}
          suffix="%"
          description="Probabilidad asignada al nivel de madurez predicho."
        />
      </div>

      {/* Maturity distribution and overall score */}
      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="rounded-2xl bg-itaca-panel p-6 shadow-card sm:p-7 lg:col-span-2">
          <h2 className="mb-4 text-[18px] font-bold text-itaca-text">
            Distribución de Madurez
          </h2>
          <DoughnutChart data={results.distribution} />
        </div>

        <div className="rounded-2xl bg-itaca-panel p-6 shadow-card sm:p-7">
          <h2 className="mb-4 text-[18px] font-bold text-itaca-text">
            Puntuación General
          </h2>
          <GaugeChart value={results.score} level={results.maturityLevel} />
          <p className="mt-3 text-center text-[13px] leading-relaxed text-itaca-subtext">
            Índice de madurez esperado, derivado de la distribución de
            probabilidades del modelo.
          </p>
        </div>
      </div>

      {/* Recommendation */}
      <div className="mt-4">
        <RecommendationCard
          recommendation={recommendation}
          personalized={results.usedPersonalization}
          onRestart={handleRestart}
        />
      </div>

      {/* Institutional call to action linking to the client's site. */}
      <section className="mt-4 flex flex-col items-center justify-between gap-4 rounded-2xl bg-itaca-blue p-6 sm:flex-row sm:gap-6">
        <div>
          <h2 className="text-[18px] font-bold text-white">
            Da el siguiente paso con Ítaca Proyectos
          </h2>
          <p className="mt-1 text-[14px] leading-relaxed text-white/90">
            Acompañamos a las empresas en su transformación y crecimiento.
          </p>
        </div>
        <Button
          href="https://proyectoitaca.co"
          target="_blank"
          rel="noopener noreferrer"
          icon={ExternalLink}
          className="w-full shrink-0 focus:ring-offset-itaca-blue sm:w-auto"
        >
          Visita nuestro sitio web
        </Button>
      </section>

      {/* Traceability: which model produced this diagnosis. */}
      <p className="mt-4 text-center text-[13px] text-itaca-subtext">
        Modelo: {results.modelVersion} · Diagnóstico {results.diagnosisId}
      </p>
    </div>
  );
}

export default DashboardPage;
