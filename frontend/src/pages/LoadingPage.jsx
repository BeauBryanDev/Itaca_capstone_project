import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import ProgressLoader from "../components/ProgressLoader.jsx";
import { useDiagnosis } from "../hooks/useDiagnosis.js";

// Second view: runs the diagnosis and shows the processing animation, then
// redirects to the results dashboard. Navigation is driven by the request
// finishing, not by a timer, so slow inference never lands on an empty
// dashboard.
function LoadingPage() {
  const navigate = useNavigate();
  const { formData, runDiagnosis } = useDiagnosis();
  const [progress, setProgress] = useState(0);
  const started = useRef(false);

  useEffect(() => {
    // Guard: if the user lands here without filling the form, go back.
    if (!formData.companyName) {
      navigate("/", { replace: true });
      return;
    }

    if (started.current) return;
    started.current = true;

    // Creep towards 90% while the request is in flight; the remaining 10% is
    // filled in once the backend actually answers.
    const interval = setInterval(() => {
      setProgress((prev) => (prev >= 90 ? prev : prev + 2));
    }, 60);

    runDiagnosis(formData).then((response) => {
      clearInterval(interval);
      setProgress(100);
      // A null response means the request failed; the form page shows the
      // error stored in the context.
      const destination = response ? "/resultados" : "/";
      setTimeout(() => navigate(destination, { replace: true }), 400);
    });

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="mx-auto flex max-w-3xl items-center justify-center px-4 py-10 sm:px-6 lg:py-16">
      <div className="w-full rounded-2xl bg-itaca-panel px-6 py-12 shadow-card sm:px-10">
        <ProgressLoader progress={progress} />
      </div>
    </div>
  );
}

export default LoadingPage;
