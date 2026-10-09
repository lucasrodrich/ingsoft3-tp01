// Suite e2e: un navegador de verdad usando la app desplegada (E2E_BASE_URL), sin mocks.
// Cada flujo interactúa, afirma sobre el dato que él mismo produjo y limpia lo que creó.
import { expect, test } from '@playwright/test'
import { PASSWORD, USUARIO_A, numeroUnico, tokenDe } from './usuarios.js'

// Entra a la app con el token del usuario de prueba (el login por pantalla se prueba aparte).
async function entrarYAbrirMesas(page, request) {
  const token = await tokenDe(request, USUARIO_A)
  await page.addInitScript((t) => localStorage.setItem('token', t), token)
  await page.goto('/mesas')
  await expect(page.getByRole('heading', { name: 'Mesas' })).toBeVisible()
}

async function crearMesa(page, numero, capacidad = 4) {
  await page.getByLabel('Número').fill(String(numero))
  await page.getByLabel('Capacidad').fill(String(capacidad))
  await page.getByRole('button', { name: 'Crear mesa' }).click()
}

async function eliminarMesa(page, numero) {
  page.once('dialog', (dialogo) => dialogo.accept())     // la app pide confirm() antes de borrar
  await page.locator('tr', { hasText: `#${numero}` }).getByRole('button', { name: 'Eliminar' }).click()
}

test('crear una mesa la muestra en la tabla, y eliminarla la saca', async ({ page, request }) => {
  await entrarYAbrirMesas(page, request)
  const numero = numeroUnico()
  await crearMesa(page, numero)
  const fila = page.locator('tr', { hasText: `#${numero}` })
  await expect(fila).toHaveCount(1)                        // el dato que ESTE test creó
  await eliminarMesa(page, numero)
  await expect(fila).toHaveCount(0)                        // y el borrado, comprobado
})

test('una mesa con número repetido muestra el error y no se duplica', async ({ page, request }) => {
  await entrarYAbrirMesas(page, request)
  const numero = numeroUnico()
  await crearMesa(page, numero)
  await expect(page.locator('tr', { hasText: `#${numero}` })).toHaveCount(1)
  try {
    await crearMesa(page, numero)                          // mismo número otra vez
    await expect(page.getByRole('alert')).toContainText('Ya existe una mesa con ese número')
    await expect(page.locator('tr', { hasText: `#${numero}` })).toHaveCount(1)   // sigue habiendo una sola
  } finally {
    await eliminarMesa(page, numero)
    await expect(page.locator('tr', { hasText: `#${numero}` })).toHaveCount(0)
  }
})

test('iniciar sesión por la pantalla lleva al panel y saluda al usuario', async ({ page, request }) => {
  await tokenDe(request, USUARIO_A)                        // asegura que el usuario de prueba exista
  await page.goto('/login')
  await page.getByLabel('Email').fill(USUARIO_A.email)
  await page.getByLabel('Contraseña').fill(PASSWORD)
  await page.getByRole('button', { name: 'Iniciar sesión' }).click()
  await expect(page).toHaveURL(/\/dashboard/)
  await expect(page.getByText(`Hola, ${USUARIO_A.nombre}`)).toBeVisible()
})
