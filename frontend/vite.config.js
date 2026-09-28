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
      // Umbral justificado en decisiones.md (TP5): hoy branches mide 85.24%
      // (la métrica más baja); 75% deja ~10 puntos de colchón real, mismo
      // criterio que el umbral del backend (revisado tras crecer la suite).
      thresholds: { statements: 75, branches: 75, functions: 75, lines: 75 },
    },
  },
});

