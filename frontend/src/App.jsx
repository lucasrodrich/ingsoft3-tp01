import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Menu from "./pages/Menu";
import Mesas from "./pages/Mesas";
import NotFound from "./pages/NotFound";
import Pedidos from "./pages/Pedidos";
import Register from "./pages/Register";
import Reservas from "./pages/Reservas";

export default function App(){return <Routes><Route path="/login" element={<Login/>}/><Route path="/register" element={<Register/>}/><Route element={<ProtectedRoute/>}><Route element={<Layout/>}><Route index element={<Navigate to="/dashboard" replace/>}/><Route path="/dashboard" element={<Dashboard/>}/><Route path="/mesas" element={<Mesas/>}/><Route path="/menu" element={<Menu/>}/><Route path="/pedidos" element={<Pedidos/>}/><Route path="/reservas" element={<Reservas/>}/></Route></Route><Route path="*" element={<NotFound/>}/></Routes>}

