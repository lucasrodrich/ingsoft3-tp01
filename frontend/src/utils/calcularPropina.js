// Sugiere un % de propina según el total (montos más altos, sugerencia más
// conservadora) y calcula cuánto le toca pagar a cada comensal si se divide
// la cuenta -- con el resto (si no divide exacto) sumado al primero.
export function sugerirPorcentajePropina(total) {
  if (!total || total <= 0) return 0;
  if (total < 5000) return 15;
  if (total < 15000) return 12;
  if (total < 40000) return 10;
  return 8;
}

export function calcularPropina(total, porcentaje) {
  if (!total || total <= 0) return 0;
  if (!porcentaje || porcentaje <= 0) return 0;
  if (porcentaje > 100) return calcularPropina(total, 100);
  const propina = Math.round((total * porcentaje) / 100);
  return propina < 1 ? 0 : propina;
}

export function dividirCuenta(totalConPropina, cantidadComensales) {
  if (!totalConPropina || totalConPropina <= 0) return [];
  if (!cantidadComensales || cantidadComensales <= 0) return [];
  if (cantidadComensales > 20) return [];
  const porPersona = Math.floor(totalConPropina / cantidadComensales);
  const resto = totalConPropina - porPersona * cantidadComensales;
  const partes = new Array(cantidadComensales).fill(porPersona);
  if (resto > 0) partes[0] += resto;
  return partes;
}
