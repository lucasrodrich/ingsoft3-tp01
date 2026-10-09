// Usuarios de prueba FIJOS, compartidos por las dos suites. Toda la app filtra los datos por usuario,
// así que cada prueba trabaja solo con lo suyo. Se registran de forma idempotente (201 la primera
// vez, 409 si ya existen). Quedan en la base de QA: la app no tiene "borrar usuario".
export const API = process.env.API_BASE_URL || 'http://localhost:8080'
export const PASSWORD = 'e2e-password-123'
export const USUARIO_A = { nombre: 'E2E Usuario A', email: 'e2e-a@restoflow-e2e.dev' }
export const USUARIO_B = { nombre: 'E2E Usuario B', email: 'e2e-b@restoflow-e2e.dev' }

export async function tokenDe(request, usuario) {
  const alta = await request.post(`${API}/api/auth/register`, { data: { ...usuario, password: PASSWORD } })
  if (![201, 409].includes(alta.status())) throw new Error(`registro de ${usuario.email}: HTTP ${alta.status()}`)
  const login = await request.post(`${API}/api/auth/login`, { data: { email: usuario.email, password: PASSWORD } })
  if (!login.ok()) throw new Error(`login de ${usuario.email}: HTTP ${login.status()}`)
  return (await login.json()).token
}

// Número de mesa que no se repite entre corridas (segundos desde 1970: cabe en un int de Postgres).
export const numeroUnico = () => Math.floor(Date.now() / 1000) + Math.floor(Math.random() * 1000)
