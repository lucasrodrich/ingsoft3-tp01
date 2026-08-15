import { Link } from "react-router-dom";
export default function NotFound(){return <div className="not-found"><span>404</span><h1>Página no encontrada.</h1><p>El lugar que buscás no existe o fue movido.</p><Link className="primary" to="/dashboard">Volver al dashboard</Link></div>}

