import { Routes, Route } from "react-router-dom";

import Login from "../pages/Login";
import Register from "../pages/Register";
import Setup from "../pages/Setup";
import Dashboard from "../pages/Dashboard";
import HomeRedirect from "../pages/HomeRedirect";


export default function AppRouter() {
    return (
        <Routes>
            <Route path="/" element={<HomeRedirect />} />

            <Route path="/setup" element={<Setup />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
    );
}