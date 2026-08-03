import api from "./api.js";

// Order of the maturity levels, lowest to highest. Matches class_map.json.
const MATURITY_LEVELS = [
  "Inicial",
  "En Desarrollo",
  "Definido",
  "Optimizado",
];

// Short descriptions shown under the maturity badge. Presentation only.
const MATURITY_DESCRIPTIONS = {
  Inicial: "Tu empresa opera de forma empírica, con poca documentación.",
  "En Desarrollo": "Tu empresa tiene procesos parcialmente documentados.",
  Definido: "Tu empresa tiene procesos estructurados y medibles.",
  Optimizado: "Tu empresa automatiza y mejora sus procesos continuamente.",
};

// Strips thousands separators so "50.000.000" becomes 50000000.
function parseBudget(value) {
  return Number(String(value).replace(/[.\s]/g, ""));
}

// Maps the camelCase form state to the snake_case payload the API expects
// (app/schemas/request.py). This is the only place where the two naming
// conventions meet.
export function toApiPayload(formData) {
  return {
    company_name: formData.companyName.trim(),
    sector: formData.companySector,
    company_size: formData.companySize,
    documented_processes_pct: Number(formData.documentedProcesses),
    annual_tech_budget: parseBudget(formData.annualBudget),
    user_response_text: formData.openAnswer.trim(),
    // Optional free text; the API expects null rather than an empty string.
    social_impact: formData.socialWork.trim() || null,
    // The LLM layer costs money per call, so it stays opt-in and off by default.
    personalize: Boolean(formData.personalize),
  };
}

// Turns the probability distribution into a 0-100 score by taking the
// expected maturity index (sum of index * probability) and rescaling it over
// the 3 gaps between the 4 levels. This is a presentation metric derived from
// real model output, not a value the backend returns.
function deriveScore(classProbabilities) {
  const expectedIndex = MATURITY_LEVELS.reduce(
    (total, level, index) => total + index * (classProbabilities[level] ?? 0),
    0
  );
  return Math.round((expectedIndex / (MATURITY_LEVELS.length - 1)) * 100);
}

// Confidence of the prediction: the probability assigned to the winning class.
function deriveConfidence(classProbabilities, maturityLevel) {
  return Math.round((classProbabilities[maturityLevel] ?? 0) * 100);
}

// Maps a DiagnosticoResponse (app/schemas/response.py) to the shape the UI
// components consume. Keeps snake_case out of the component tree.
export function fromApiResponse(data) {
  const classProbabilities = data.class_probabilities ?? {};
  const maturityLevel = data.maturity_level;

  return {
    diagnosisId: data.diagnostico_id,
    maturityLevel,
    maturityDescription: MATURITY_DESCRIPTIONS[maturityLevel] ?? "",
    score: deriveScore(classProbabilities),
    confidence: deriveConfidence(classProbabilities, maturityLevel),
    // Recharts consumes an array of {name, value}; values as whole percentages.
    distribution: MATURITY_LEVELS.map((level) => ({
      name: level,
      value: Math.round((classProbabilities[level] ?? 0) * 100),
    })),
    // The personalized text is only present when the LLM layer ran and
    // succeeded; otherwise the deterministic catalog recommendation is shown.
    recommendation: data.personalized_recommendation ?? data.base_recommendation,
    usedPersonalization: data.used_personalization,
    modelVersion: data.model_version,
    createdAt: data.created_at,
  };
}

// Sends the company form to the backend and returns the mapped diagnosis.
// Throws on failure: callers decide how to surface the error to the user.
export async function submitDiagnosis(formData) {
  const { data } = await api.post("/diagnostico", toApiPayload(formData));
  return fromApiResponse(data);
}

// Retrieves a previously persisted diagnosis by its identifier.
export async function getDiagnosis(diagnosisId) {
  const { data } = await api.get(`/diagnostico/${diagnosisId}`);
  return fromApiResponse(data);
}

// Reports whether the backend is up and its artifacts are loaded.
export async function checkHealth() {
  const { data } = await api.get("/health");
  return data;
}
