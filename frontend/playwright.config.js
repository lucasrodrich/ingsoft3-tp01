import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',                // recoge los DOS archivos; cada job del pipeline corre el suyo por nombre
  timeout: 60_000,                 // tope de CADA test: generoso para el cold start de Render
  expect: { timeout: 15_000 },     // tope de CADA aserción (el default es 5 s)
  workers: 1,                      // las dos suites comparten la base de QA: en serie no se pisan entre sí
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',   // el FRONT; la api tiene su propia variable: API_BASE_URL
    trace: 'on-first-retry',         // la traza se graba en el retry de un fallo (los verdes no la generan)
    screenshot: 'only-on-failure',   // screenshot de cada fallo en el reporte
  },
  retries: 1,                      // 1 retry: absorbe una demora suelta; si pasa recién ahí, el reporte lo marca flaky
  reporter: [['html', { open: 'never' }], ['list']],
})
