import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, describe, expect, it, vi } from "vitest";
import Mesas from "../src/pages/Mesas";

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

describe("Mesas", () => {
  afterEach(() => vi.restoreAllMocks());

  // Regresion (Sentry, RESTOFLOW-FRONT-1): useEffect(load, []) devolvia la Promise de load, y React la
  // toma como funcion de limpieza. Al salir de Mesas (ir a Menu) intentaba ejecutarla y la app quedaba en blanco.
  it("se puede desmontar (salir de la pantalla) sin romper", async () => {
    global.fetch = vi.fn().mockResolvedValue({ status: 200, ok: true, json: async () => [] });
    const root = createRoot(document.createElement("div"));
    await act(async () => root.render(<Mesas />));
    await expect(act(async () => root.unmount())).resolves.not.toThrow();
  });
});
