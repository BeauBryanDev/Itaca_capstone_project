import axios from "axios";

// Centralized HTTP client configuration.
// The backend (FastAPI) runs on port 8005 and mounts its routers at the root,
// so there is no "/api" prefix. Override with VITE_API_URL when deploying.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8005",
  headers: {
    "Content-Type": "application/json",
  },
  // Inference loads a Keras model and can take a few seconds on a cold call.
  timeout: 30000,
});

// Translates any axios failure into a single Error carrying a message that is
// safe to show to the user in Spanish. Components never inspect axios internals.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = "No pudimos completar el diagnóstico. Intenta de nuevo.";

    if (error.response) {
      const { status, data } = error.response;
      if (status === 422) {
        // FastAPI returns either a validation error list or a plain detail
        // string (for example when the recommendation catalog has no match).
        message = Array.isArray(data?.detail)
          ? "Revisa los datos del formulario: algún valor no es válido."
          : data?.detail || "Los datos enviados no son válidos.";
      } else if (status === 404) {
        message = "No encontramos el diagnóstico solicitado.";
      } else if (status >= 500) {
        message = "El servidor tuvo un problema procesando tu diagnóstico.";
      }
    } else if (error.code === "ECONNABORTED") {
      message = "El diagnóstico tardó demasiado. Intenta de nuevo.";
    } else if (error.request) {
      message =
        "No pudimos conectar con el servidor. Verifica que el backend esté activo.";
    }

    const normalized = new Error(message);
    normalized.status = error.response?.status ?? null;
    normalized.cause = error;
    return Promise.reject(normalized);
  }
);

export default api;
