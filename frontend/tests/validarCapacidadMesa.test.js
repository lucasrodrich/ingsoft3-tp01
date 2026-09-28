import { describe, expect, it } from "vitest";
import { sugerirMesa, validarCapacidadMesa } from "../src/utils/validarCapacidadMesa";

describe("validarCapacidadMesa", () => {
  it.each([
    ["faltan datos", { capacidadMesa: 0, cantidadPersonas: 2 }, "Completá la mesa y la cantidad de personas."],
    ["cantidad en cero", { capacidadMesa: 4, cantidadPersonas: 0 }, "Completá la mesa y la cantidad de personas."],
    ["supera la capacidad", { capacidadMesa: 4, cantidadPersonas: 6 }, "Esa mesa admite hasta 4 personas."],
    ["sobran demasiados lugares", { capacidadMesa: 10, cantidadPersonas: 2 }, "Elegí una mesa más chica: sobran demasiados lugares."],
    ["capacidad justa", { capacidadMesa: 4, cantidadPersonas: 4 }, ""],
  ])("%s", (_caso, entrada, mensajeEsperado) => {
    expect(validarCapacidadMesa(entrada)).toBe(mensajeEsperado);
  });

  it("rechaza cantidades negativas aunque haya mesa", () => {
    expect(validarCapacidadMesa({ capacidadMesa: 4, cantidadPersonas: -1 })).toBe(
      "La cantidad de personas debe ser mayor a cero."
    );
  });
});

describe("sugerirMesa", () => {
  const mesas = [
    { id: 1, capacidad: 2 },
    { id: 2, capacidad: 4 },
    { id: 3, capacidad: 8 },
  ];

  it("sugiere la mesa más chica que alcanza para el grupo", () => {
    expect(sugerirMesa(mesas, 3)).toEqual({ id: 2, capacidad: 4 });
  });

  it("devuelve null si ninguna mesa alcanza", () => {
    expect(sugerirMesa(mesas, 20)).toBeNull();
  });

  it("devuelve null ante datos inválidos, sin explotar", () => {
    expect(sugerirMesa([], 2)).toBeNull();
    expect(sugerirMesa(mesas, 0)).toBeNull();
    expect(sugerirMesa(null, 2)).toBeNull();
  });
});
