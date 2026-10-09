// Suite de INTEGRACIÓN: le habla a la API desplegada (API_BASE_URL) con su base de datos de verdad.
// Sin navegador, sin dobles. Cada prueba que crea datos usa un número de mesa que no se repite y
// borra lo que creó, comprobándolo.
import { expect, test } from '@playwright/test'
import { API, USUARIO_A, USUARIO_B, numeroUnico, tokenDe } from './usuarios.js'

const auth = (token) => ({ Authorization: `Bearer ${token}` })
const listar = async (request, token) =>
  (await (await request.get(`${API}/api/mesas`, { headers: auth(token) })).json())

test('alta, lectura y borrado de una mesa pasan por la base de verdad', async ({ request }) => {
  const token = await tokenDe(request, USUARIO_A)
  const numero = numeroUnico()
  let id
  try {
    const alta = await request.post(`${API}/api/mesas`, { headers: auth(token), data: { numero, capacidad: 4 } })
    expect(alta.status()).toBe(201)
    id = (await alta.json()).id

    expect((await listar(request, token)).some((m) => m.numero === numero)).toBe(true)   // el GET encuentra lo creado

    const baja = await request.delete(`${API}/api/mesas/${id}`, { headers: auth(token) })
    expect(baja.status()).toBe(204)
    expect((await listar(request, token)).some((m) => m.numero === numero)).toBe(false)  // y ya no está
  } finally {
    if (id) await request.delete(`${API}/api/mesas/${id}`, { headers: auth(token) })      // red de seguridad
  }
})

test('una mesa con capacidad 0 se rechaza y no se crea nada', async ({ request }) => {
  const token = await tokenDe(request, USUARIO_A)
  const numero = numeroUnico()
  const alta = await request.post(`${API}/api/mesas`, { headers: auth(token), data: { numero, capacidad: 0 } })
  expect(alta.status()).toBe(422)    // esta API contesta 422 ante datos inválidos
  expect((await listar(request, token)).some((m) => m.numero === numero)).toBe(false)
})

test('un usuario no puede ver ni encontrar la mesa de otro', async ({ request }) => {
  const tokenA = await tokenDe(request, USUARIO_A)
  const tokenB = await tokenDe(request, USUARIO_B)
  const numero = numeroUnico()
  let id
  try {
    const alta = await request.post(`${API}/api/mesas`, { headers: auth(tokenA), data: { numero, capacidad: 2 } })
    expect(alta.status()).toBe(201)
    id = (await alta.json()).id

    const ajena = await request.get(`${API}/api/mesas/${id}`, { headers: auth(tokenB) })
    expect(ajena.status()).toBe(404)                                                       // B no la ve (ni sabe que existe)
    expect((await listar(request, tokenB)).some((m) => m.numero === numero)).toBe(false)
    expect((await request.get(`${API}/api/mesas/${id}`, { headers: auth(tokenA) })).status()).toBe(200)  // A sigue viéndola
  } finally {
    if (id) await request.delete(`${API}/api/mesas/${id}`, { headers: auth(tokenA) })
  }
})
