export function validateLogin({ email, password }) {
  if (!email || !password) return "Completá email y contraseña.";
  if (!/^\S+@\S+\.\S+$/.test(email)) return "Ingresá un email válido.";
  return "";
}
export function validateRegister({ nombre, email, password, confirmPassword }) {
  if (!nombre || !email || !password || !confirmPassword) return "Completá todos los campos.";
  if (nombre.trim().length < 2) return "El nombre debe tener al menos 2 caracteres.";
  if (!/^\S+@\S+\.\S+$/.test(email)) return "Ingresá un email válido.";
  if (password.length < 8) return "La contraseña debe tener al menos 8 caracteres.";
  if (password !== confirmPassword) return "Las contraseñas no coinciden.";
  return "";
}

