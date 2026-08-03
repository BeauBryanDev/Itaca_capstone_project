import { createContext, useState } from "react";
import { submitDiagnosis } from "../services/diagnosisService.js";

// Global state for the diagnosis flow: form data, loading, results and error.
export const DiagnosisContext = createContext(null);

const initialFormData = {
  companyName: "",
  companySector: "",
  companySize: "",
  documentedProcesses: "",
  annualBudget: "",
  openAnswer: "",
  socialWork: "",
  personalize: false,
};

export function DiagnosisProvider({ children }) {
  const [formData, setFormData] = useState(initialFormData);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState(null);

  // Updates a single field of the form.
  function updateField(name, value) {
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  // Sends the form to the backend. On failure it stores the error and returns
  // null, so the UI shows a real error instead of fabricated results and a
  // broken integration is always visible.
  async function runDiagnosis(data) {
    setLoading(true);
    setError(null);
    try {
      const response = await submitDiagnosis(data);
      setResults(response);
      setRecommendation(response.recommendation);
      return response;
    } catch (requestError) {
      setError(requestError.message);
      setResults(null);
      setRecommendation(null);
      return null;
    } finally {
      setLoading(false);
    }
  }

  // Clears everything to start a new diagnosis.
  function resetDiagnosis() {
    setFormData(initialFormData);
    setResults(null);
    setRecommendation(null);
    setError(null);
    setLoading(false);
  }

  const value = {
    formData,
    setFormData,
    updateField,
    loading,
    setLoading,
    results,
    setResults,
    recommendation,
    setRecommendation,
    error,
    setError,
    runDiagnosis,
    resetDiagnosis,
  };

  return (
    <DiagnosisContext.Provider value={value}>
      {children}
    </DiagnosisContext.Provider>
  );
}
