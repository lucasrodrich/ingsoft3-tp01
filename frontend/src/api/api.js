const TOKEN_KEY = "token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const saveToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.body ? { "Content-Type": "application/json" } : {}), ...options.headers };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`/api${path}`, { ...options, headers });
  if (response.status === 401 && token) {
    clearToken();
    window.dispatchEvent(new Event("auth:unauthorized"));
  }
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error || "No se pudo completar la operación.");
    error.status = response.status; error.details = data.details;
    throw error;
  }
  return data;
}

const json = (method, body) => ({ method, body: JSON.stringify(body) });
const query = (params = {}) => {
  const values = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value !== "" && value != null) values.set(key, value); });
  const text = values.toString(); return text ? `?${text}` : "";
};

export const authApi = {
  register: (data) => apiFetch("/auth/register", json("POST", data)),
  login: (data) => apiFetch("/auth/login", json("POST", data)),
  me: () => apiFetch("/auth/me"),
};
export const getDashboard = () => apiFetch("/dashboard");
export const mesasApi = {
  list: () => apiFetch("/mesas"), create: (x) => apiFetch("/mesas", json("POST", x)),
  update: (id, x) => apiFetch(`/mesas/${id}`, json("PUT", x)),
  state: (id, estado) => apiFetch(`/mesas/${id}/estado`, json("PATCH", { estado })),
  remove: (id) => apiFetch(`/mesas/${id}`, { method: "DELETE" }),
};
export const categoriasApi = {
  list: () => apiFetch("/categorias"), create: (x) => apiFetch("/categorias", json("POST", x)),
  update: (id, x) => apiFetch(`/categorias/${id}`, json("PUT", x)),
  remove: (id) => apiFetch(`/categorias/${id}`, { method: "DELETE" }),
};
export const productosApi = {
  list: (p) => apiFetch(`/productos${query(p)}`), create: (x) => apiFetch("/productos", json("POST", x)),
  update: (id, x) => apiFetch(`/productos/${id}`, json("PUT", x)),
  availability: (id, disponible) => apiFetch(`/productos/${id}/disponibilidad`, json("PATCH", { disponible })),
  remove: (id) => apiFetch(`/productos/${id}`, { method: "DELETE" }),
};
export const pedidosApi = {
  list: (p) => apiFetch(`/pedidos${query(p)}`), get: (id) => apiFetch(`/pedidos/${id}`),
  create: (x) => apiFetch("/pedidos", json("POST", x)), state: (id, estado) => apiFetch(`/pedidos/${id}/estado`, json("PATCH", { estado })),
  remove: (id) => apiFetch(`/pedidos/${id}`, { method: "DELETE" }),
  addItem: (id, x) => apiFetch(`/pedidos/${id}/items`, json("POST", x)),
  updateItem: (id, itemId, cantidad) => apiFetch(`/pedidos/${id}/items/${itemId}`, json("PUT", { cantidad })),
  removeItem: (id, itemId) => apiFetch(`/pedidos/${id}/items/${itemId}`, { method: "DELETE" }),
};
export const reservasApi = {
  list: (p) => apiFetch(`/reservas${query(p)}`), create: (x) => apiFetch("/reservas", json("POST", x)),
  update: (id, x) => apiFetch(`/reservas/${id}`, json("PUT", x)), state: (id, estado) => apiFetch(`/reservas/${id}/estado`, json("PATCH", { estado })),
  remove: (id) => apiFetch(`/reservas/${id}`, { method: "DELETE" }),
};

