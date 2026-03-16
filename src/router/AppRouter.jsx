import { Routes, Route, Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { FaShieldHalved } from "react-icons/fa6";
import useAuthStore from "../store/authStore";

import Login from "../pages/Login";
import Register from "../pages/Register";
import Setup from "../pages/Setup";
import Dashboard from "../pages/Dashboard";
import HomeRedirect from "../pages/HomeRedirect";

const BASE_URL = process.env.REACT_APP_API_URL;

const ProtectedRoute = ({ children }) => {
    const isAuthenticated = useAuthStore(state => state.isAuthenticated);
    const user = useAuthStore(state => state.user);
    if (!isAuthenticated) return <Navigate to="/login" replace />;
    if (user && !user.is_approved) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#020617] p-6">
                <div className="p-10 border border-white/5 bg-[#0a0f1e] shadow-2xl text-center max-w-md">
                    <div className="h-12 w-12 bg-amber-600 mx-auto flex items-center justify-center mb-6">
                        <FaShieldHalved className="text-white text-xl" />
                    </div>
                    <h2 className="text-xl font-black text-white uppercase tracking-tighter mb-4">Erişim Kısıtlı</h2>
                    <p className="text-[11px] font-bold text-slate-500 uppercase tracking-widest leading-relaxed">Yönetici onayı bekleniyor.</p>
                    <button onClick={() => window.location.reload()} className="mt-8 w-full py-4 bg-blue-600 text-white text-[10px] font-black uppercase tracking-widest hover:bg-blue-500">DURUMU GÜNCELLE</button>
                </div>
            </div>
        );
    }
    return children;
};

export default function AppRouter() {
    const [setupRequired, setSetupRequired] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        let isMounted = true;
        fetch(`${BASE_URL}/setup-status/`)
            .then(res => res.json())
            .then(data => {
                if (isMounted) {
                    setSetupRequired(data.setup_required === true);
                    setLoading(false);
                }
            })
            .catch(() => {
                if (isMounted) {
                    setError(true);
                    setLoading(false);
                }
            });
        return () => { isMounted = false; };
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-[#020617] flex items-center justify-center">
                <div className="h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-[#020617] flex flex-col items-center justify-center p-6 text-center">
                <p className="text-rose-500 font-bold uppercase tracking-widest text-xs mb-4">Bağlantı Hatası</p>
                <button onClick={() => window.location.reload()} className="px-6 py-2 border border-white/10 text-white text-[10px] font-black uppercase">Yeniden Dene</button>
            </div>
        );
    }

    return (
        <Routes>
            {setupRequired === true ? (
                <>
                    <Route path="/setup" element={<Setup />} />
                    <Route path="*" element={<Navigate to="/setup" replace />} />
                </>
            ) : (
                <>
                    <Route path="/" element={<HomeRedirect />} />
                    <Route path="/setup" element={<Navigate to="/login" replace />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/dashboard" element={
                        <ProtectedRoute>
                            <Dashboard />
                        </ProtectedRoute>
                    } />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </>
            )}
        </Routes>
    );
}