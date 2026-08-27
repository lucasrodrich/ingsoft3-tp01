import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const links = [["/dashboard", "Resumen"], ["/mesas", "Mesas"], ["/menu", "Menú"], ["/pedidos", "Pedidos"], ["/reservas", "Reservas"]];
export default function Layout() {
  const { user, logout } = useAuth(); const navigate = useNavigate();
  const exit = () => { logout(); navigate("/login"); };
  return <div className="shell">
    <aside className="sidebar"><div className="brand"><span>R</span><div>RestoFlow<small>Gestión integral</small></div></div>
      <nav>{links.map(([to, name]) => <NavLink key={to} to={to}>{name}</NavLink>)}</nav>
      <button className="link-button" onClick={exit}>Cerrar sesión</button>
    </aside>
    <main className="main"><header><div><small>RESTOFLOW</small><strong>Hola, {user?.nombre}</strong></div><button className="mobile-exit" onClick={exit}>Salir</button></header><Outlet /></main>
  </div>;
}

