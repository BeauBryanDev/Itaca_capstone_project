import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // The backend only allows http://localhost:5173 in CORS_ALLOWED_ORIGINS
    // (app/core/config.py). strictPort makes Vite fail loudly instead of
    // silently moving to 5174 and breaking every request with a CORS error.
    port: 5173,
    strictPort: true,
  },
});
