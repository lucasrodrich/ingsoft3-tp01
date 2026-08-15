import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import ErrorMessage from "../components/ErrorMessage";
import { validateRegister } from "../utils/validation";

export default function Register() {
  const { user, register } = useAuth(); const navigate = useNavigate();
  const [form,setForm]=useState({nombre:"",email:"",password:"",confirmPassword:""}); const [error,setError]=useState(""); const [loading,setLoading]=useState(false);
  if(user) return <Navigate to="/dashboard" replace/>;
  const change=e=>setForm({...form,[e.target.name]:e.target.value});
  const submit=async e=>{e.preventDefault();const message=validateRegister(form);if(message)return setError(message);setLoading(true);setError("");try{const {confirmPassword,...data}=form;await register(data);navigate("/dashboard");}catch(err){setError(err.message);}finally{setLoading(false);}};
  return <div className="auth-page"><section className="auth-visual"><div><span className="eyebrow">EMPEZÁ HOY</span><h1>Una operación<br/>más ordenada.</h1><p>Creá tu espacio y obtené categorías de menú listas para usar.</p></div></section><section className="auth-panel"><form className="auth-card" onSubmit={submit}><div className="brand auth-brand"><span>R</span><div>Restaurante<small>Gestión integral</small></div></div><h2>Crear cuenta</h2><ErrorMessage error={error}/>{[["nombre","Nombre","text"],["email","Email","email"],["password","Contraseña","password"],["confirmPassword","Confirmar contraseña","password"]].map(([name,label,type])=><label key={name}>{label}<input name={name} type={type} value={form[name]} onChange={change}/></label>)}<button className="primary full" disabled={loading}>{loading?"Creando...":"Crear cuenta"}</button><p className="center">¿Ya tenés cuenta? <Link to="/login">Iniciar sesión</Link></p></form></section></div>;
}

