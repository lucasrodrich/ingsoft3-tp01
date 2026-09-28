import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://localhost:8080", "/health": "http://localhost:8080" } },
  test: {
    environment: "jsdom",
    globals: true,
    coverage: {
      provider: "v8",
      include: ["src/utils/**", "src/api/client.js"],
      reporter: ["text", "html"],
      // Umbral justificado en decisiones.md (TP5): hoy branches mide 66.66%
      // (la métrica más baja); 55% deja margen real sobre las 4 métricas.
      thresholds: { statements: 55, branches: 55, functions: 55, lines: 55 },
    },
  },
});

