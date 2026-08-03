import { useNavigate } from "react-router-dom";
import { AlertCircle } from "lucide-react";
import Stepper from "../components/Stepper.jsx";
import HeroCard from "../components/HeroCard.jsx";
import CompanyForm from "../components/CompanyForm.jsx";
import { useDiagnosis } from "../hooks/useDiagnosis.js";

// First view: company form with the hero card (desktop) and stepper (mobile).
function DiagnosisPage() {
  const navigate = useNavigate();
  const { error } = useDiagnosis();

  function handleSubmit() {
    // The diagnosis itself runs on the loading page.
    navigate("/procesando");
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-10">
      {/* Mobile stepper */}
      <div className="mb-6 lg:hidden">
        <Stepper current={1} />
      </div>

      {/* Mobile heading - hidden on desktop */}
      <div className="mb-5 lg:hidden">
        <h1 className="text-[28px] font-bold leading-tight text-itaca-text">
          Autodiagnóstico Empresarial
        </h1>
        <p className="mt-2 text-[15px] leading-relaxed text-itaca-subtext">
          Descubre el nivel de madurez digital de tu empresa en pocos minutos.
        </p>
      </div>

      {/* Shown when a previous attempt failed and sent the user back here. */}
      {error && (
        <div
          role="alert"
          className="mb-5 flex items-start gap-3 rounded-xl border border-itaca-red/40 bg-itaca-red/10 p-4"
        >
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-itaca-red" />
          <p className="text-[14px] leading-relaxed text-itaca-text">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <HeroCard />
        <CompanyForm onSubmit={handleSubmit} />
      </div>
    </div>
  );
}

export default DiagnosisPage;
