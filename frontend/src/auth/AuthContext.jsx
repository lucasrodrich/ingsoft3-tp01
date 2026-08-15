import { createContext, useContext, useEffect, useState } from "react";
import { authApi, clearToken, getToken, saveToken } from "../api/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getToken()));

  const logout = () => { clearToken(); setUser(null); };
  useEffect(() => {
    const restore = async () => {
      if (!getToken()) return setLoading(false);
      try { setUser(await authApi.me()); } catch { logout(); } finally { setLoading(false); }
    };
    restore();
    const unauthorized = () => { setUser(null); window.location.assign("/login"); };
    window.addEventListener("auth:unauthorized", unauthorized);
    return () => window.removeEventListener("auth:unauthorized", unauthorized);
  }, []);

  const authenticate = async (fn, data) => {
    const result = await fn(data); saveToken(result.token); setUser(result.user); return result;
  };
  return <AuthContext.Provider value={{ user, loading, login: (x) => authenticate(authApi.login, x), register: (x) => authenticate(authApi.register, x), logout }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);

