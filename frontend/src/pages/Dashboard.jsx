import { useEffect, useState } from "react";
import { getDashboard } from "../api/api";
import ErrorMessage from "../components/ErrorMessage";
import Loading from "../components/Loading";
import { formatCurrency } from "../utils/formatCurrency";

const cards=[['mesasDisponibles','Mesas disponibles','Disponible'],['mesasOcupadas','Mesas ocupadas','En servicio'],['mesasReservadas','Mesas reservadas','Marcadas ahora'],['pedidosAbiertos','Pedidos abiertos','En curso'],['reservasHoy','Reservas de hoy','Pendientes y confirmadas'],['ventasHoy','Ventas de hoy','Pedidos cerrados'],['pedidosHoy','Pedidos de hoy','Excepto cancelados']];
export default function Dashboard(){const[data,setData]=useState(null);const[error,setError]=useState("");useEffect(()=>{getDashboard().then(setData).catch(e=>setError(e.message));},[]);return <section><div className="page-title"><div><span className="eyebrow">PANORAMA GENERAL</span><h1>Dashboard</h1><p>Así está funcionando tu restaurante hoy.</p></div></div><ErrorMessage error={error}/>{!data&&!error?<Loading/>:<div className="metric-grid">{data&&cards.map(([key,title,detail],i)=><article className={`metric metric-${i}`} key={key}><small>{title}</small><strong>{key==='ventasHoy'?formatCurrency(data[key]):data[key]}</strong><span>{detail}</span></article>)}</div>}</section>}

