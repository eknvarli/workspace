import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { FaShieldHalved } from "react-icons/fa6";
import useAuthStore from "../store/authStore";
import api from "../api/axios";

import Login from "../pages/Login";
import Register from "../pages/Register";
import Setup from "../pages/Setup";
import Dashboard from "../pages/Dashboard";
import HomeRedirect from "../pages/HomeRedirect";

const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, user } = useAuthStore();
    if (!isAuthenticated) return <Navigate to="/login" replace />;
    if (user && !user.is_approved) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#020617] p-6">
                <div className="p-10 border border-white/5 bg-[#0a0f1e] shadow-2xl text-center max-w-md">
                    <div className="h-12 w-12 bg-amber-600 mx-auto flex items-center justify-center mb-6">
                        <FaShieldHalved className="text-white text-xl" />
                    </div>
                    <h2 className="text-xl font-black text-white uppercase tracking-tighter mb-4">Erişim Kısıtlı</h2>
                    <p className="text-[11px] font-bold text-slate-500 uppercase tracking-widest leading-relaxed">Hesabınız oluşturuldu ancak dashboard'a erişmek için yönetici onayı bekleniyor.</p>
                    <button onClick={() => window.location.reload()} className="mt-8 w-full py-4 bg-blue-600 text-white text-[10px] font-black uppercase tracking-widest hover:bg-blue-500 transition-colors">DURUMU GÜNCELLE</button>
                </div>
            </div>
        );
    }
    return children;
};

export default function AppRouter() {
    const { isSetupRequired, setSetupRequired } = useAuthStore();
    const [loading, setLoading] = useState(true);
    const location = useLocation();

    useEffect(() => {
        const checkSetup = async () => {
            try {
                const response = await api.get("/setup-status/");
                setSetupRequired(response.data.setup_required);
            } catch (error) {
                console.error("Failed to check setup status", error);
            } finally {
                setLoading(false);
            }
        };
        checkSetup();
    }, [setSetupRequired]);

    if (loading) {
        return (
            <div className="min-h-screen bg-[#020617] flex items-center justify-center">
                <div className="h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (isSetupRequired) {
        if (location.pathname !== "/setup") {
            return <Navigate to="/setup" replace />;
        }
    } else {
        if (location.pathname === "/setup") {
            return <Navigate to="/login" replace />;
        }
    }

    return (
        <Routes>
            <Route path="/" element={<HomeRedirect />} />
            <Route path="/setup" element={<Setup />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={
                <ProtectedRoute>
                    <Dashboard />
                </ProtectedRoute>
            } />
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}