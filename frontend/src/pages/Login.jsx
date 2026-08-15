import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import ErrorMessage from "../components/ErrorMessage";
import { validateLogin } from "../utils/validation";

export default function Login() {
  const { user, login } = useAuth(); const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" }); const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  if (user) return <Navigate to="/dashboard" replace />;
  const submit = async (e) => { e.preventDefault(); const message = validateLogin(form); if (message) return setError(message);
    setLoading(true); setError(""); try { await login(form); navigate("/dashboard"); } catch (err) { setError(err.message); } finally { setLoading(false); } };
  return <div className="auth-page"><section className="auth-visual"><div><span className="eyebrow">ADMINISTRACIÓN SIMPLE</span><h1>Tu restaurante,<br/>bajo control.</h1><p>Mesas, menú, pedidos y reservas en un único lugar.</p></div></section>
    <section className="auth-panel"><form className="auth-card" onSubmit={submit}><div className="brand auth-brand"><span>R</span><div>Restaurante<small>Gestión integral</small></div></div><h2>Bienvenido</h2><p>Ingresá para gestionar tu restaurante.</p><ErrorMessage error={error}/>
      <label>Email<input type="email" autoComplete="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} placeholder="tu@email.com"/></label>
      <label>Contraseña<input type="password" autoComplete="current-password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} placeholder="••••••••"/></label>
      <button className="primary full" disabled={loading}>{loading ? "Ingresando..." : "Iniciar sesión"}</button><p className="center">¿No tenés cuenta? <Link to="/register">Crear cuenta</Link></p></form></section></div>;
}

