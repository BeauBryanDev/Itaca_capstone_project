import { useContext } from "react";
import { DiagnosisContext } from "../store/DiagnosisContext.jsx";

// Convenience hook to read the diagnosis context from any component.
export function useDiagnosis() {
  const context = useContext(DiagnosisContext);
  if (!context) {
    throw new Error("useDiagnosis debe usarse dentro de <DiagnosisProvider>");
  }
  return context;
}
