import { beforeEach, describe, expect, it, vi } from "vitest";
import { clearToken, getToken, saveToken, apiFetch } from "../src/api/api";
import { formatCurrency } from "../src/utils/formatCurrency";
import { formatDate } from "../src/utils/formatDate";
import { validateLogin, validateRegister } from "../src/utils/validation";

describe("utilidades",()=>{
  beforeEach(()=>localStorage.clear());
  it("formatea moneda ARS",()=>expect(formatCurrency(18500)).toMatch(/18[.]500/));
  it("formatea fechas",()=>expect(formatDate("2026-08-14")).toBe("14/08/2026"));
  it("valida login",()=>{expect(validateLogin({email:"",password:""})).toBeTruthy();expect(validateLogin({email:"a@b.com",password:"x"})).toBe("")});
  it("valida registro y coincidencia",()=>{expect(validateRegister({nombre:"Ana",email:"a@b.com",password:"12345678",confirmPassword:"87654321"})).toContain("coinciden");expect(validateRegister({nombre:"Ana",email:"a@b.com",password:"12345678",confirmPassword:"12345678"})).toBe("")});
  it("guarda y elimina token",()=>{saveToken("abc");expect(getToken()).toBe("abc");clearToken();expect(getToken()).toBeNull()});
  it("envía Authorization y maneja errores",async()=>{saveToken("abc");global.fetch=vi.fn().mockResolvedValue({status:400,ok:false,json:async()=>({error:"Fallo"})});await expect(apiFetch("/test")).rejects.toThrow("Fallo");expect(fetch.mock.calls[0][1].headers.Authorization).toBe("Bearer abc")});
});

