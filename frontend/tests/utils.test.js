import { beforeEach, describe, expect, it, vi } from "vitest";
import { clearToken, getToken, saveToken, apiFetch } from "../src/api/api";
import { formatCurrency } from "../src/utils/formatCurrency";
import { formatDate } from "../src/utils/formatDate";
import { validateLogin, validateRegister } from "../src/utils/validation";

describe("utilidades",()=>{
  beforeEach(()=>localStorage.clear());
  it("formatea moneda ARS",()=>expect(formatCurrency(18500)).toMatch(/18[.]500/));
  it("formatea fechas",()=>expect(formatDate("2026-08-14")).toBe("14/08/2026"));
  it.each([
    ["campos vacíos", { email: "", password: "" }, "Completá email y contraseña."],
    ["email sin arroba", { email: "no-es-un-email", password: "x" }, "Ingresá un email válido."],
    ["datos válidos", { email: "a@b.com", password: "x" }, ""],
  ])("valida login: %s", (_caso, entrada, mensajeEsperado) => {
    expect(validateLogin(entrada)).toBe(mensajeEsperado);
  });

  it("rechaza el registro cuando las contraseñas no coinciden", () => {
    const resultado = validateRegister({ nombre: "Ana", email: "a@b.com", password: "12345678", confirmPassword: "87654321" });
    expect(resultado).toContain("coinciden");
  });

  it("acepta un registro con todos los datos válidos y coincidentes", () => {
    const resultado = validateRegister({ nombre: "Ana", email: "a@b.com", password: "12345678", confirmPassword: "12345678" });
    expect(resultado).toBe("");
  });
  it("guarda y elimina token",()=>{saveToken("abc");expect(getToken()).toBe("abc");clearToken();expect(getToken()).toBeNull()});
  it("envía Authorization y maneja errores",async()=>{saveToken("abc");global.fetch=vi.fn().mockResolvedValue({status:400,ok:false,json:async()=>({error:"Fallo"})});await expect(apiFetch("/test")).rejects.toThrow("Fallo");expect(fetch.mock.calls[0][1].headers.Authorization).toBe("Bearer abc")});

  it("devuelve los datos parseados cuando la respuesta es exitosa", async () => {
    // Arrange: un fetch doble que contesta 200 con un body válido
    global.fetch = vi.fn().mockResolvedValue({ status: 200, ok: true, json: async () => ({ id: 1, nombre: "Mesa 1" }) });

    // Act
    const resultado = await apiFetch("/mesas/1");

    // Assert
    expect(resultado).toEqual({ id: 1, nombre: "Mesa 1" });
  });

  it("ante un 401 con token guardado, lo borra y avisa al resto de la app", async () => {
    // Arrange
    saveToken("token-vencido");
    global.fetch = vi.fn().mockResolvedValue({ status: 401, ok: false, json: async () => ({}) });
    const avisoDeSesionVencida = vi.fn();
    window.addEventListener("auth:unauthorized", avisoDeSesionVencida);

    // Act
    await apiFetch("/mesas").catch(() => {}); // el 401 también rechaza la promesa; acá solo interesa el efecto secundario

    // Assert: la interacción, no el valor de retorno -- por eso es un mock y no un stub
    expect(getToken()).toBeNull();
    expect(avisoDeSesionVencida).toHaveBeenCalledOnce();

    window.removeEventListener("auth:unauthorized", avisoDeSesionVencida);
  });
});

