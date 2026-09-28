// Validación client-side de la reserva contra la capacidad de la mesa elegida,
// para avisarle al usuario antes de mandar el POST (el backend igual la
// vuelve a validar: esto es sólo mejor feedback, no la única guarda).
export function validarCapacidadMesa({ capacidadMesa, cantidadPersonas }) {
  if (!capacidadMesa || !cantidadPersonas) return "Completá la mesa y la cantidad de personas.";
  if (cantidadPersonas <= 0) return "La cantidad de personas debe ser mayor a cero.";
  if (cantidadPersonas > capacidadMesa) return `Esa mesa admite hasta ${capacidadMesa} personas.`;
  if (capacidadMesa - cantidadPersonas >= 5) return "Elegí una mesa más chica: sobran demasiados lugares.";
  return "";
}

// Sugiere, entre las mesas libres, la de menor capacidad que igual alcance
// para el grupo -- para no ofrecer una mesa de 8 a una reserva de 2.
export function sugerirMesa(mesasDisponibles, cantidadPersonas) {
  if (!Array.isArray(mesasDisponibles) || mesasDisponibles.length === 0) return null;
  if (!cantidadPersonas || cantidadPersonas <= 0) return null;
  const queAlcanzan = mesasDisponibles.filter((m) => m.capacidad >= cantidadPersonas);
  if (queAlcanzan.length === 0) return null;
  return queAlcanzan.reduce((mejor, actual) => (actual.capacidad < mejor.capacidad ? actual : mejor));
}
