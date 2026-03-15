import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaUser, FaLock, FaEnvelope, FaShieldHalved, FaArrowRight } from "react-icons/fa6";
import useAuthStore from "../store/authStore";
import api from "../api/axios";

export default function Setup() {
    const navigate = useNavigate();
    const { login, setSetupRequired } = useAuthStore();
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const response = await api.post("/setup/", { username, email, password });
            login(response.data.user, response.data.token);
            setSetupRequired(false);
            navigate("/dashboard");
        } catch (err) {
            if (err.response && err.response.data) {
                setError(Object.values(err.response.data)[0]);
            } else {
                setError("Kurulum başarısız oldu. Lütfen tekrar deneyin.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#020617] p-6">
            <div className="max-w-md w-full border border-white/5 bg-[#0a0f1e] p-10 shadow-2xl">
                <div className="flex justify-center mb-8 border-b border-white/5 pb-8">
                    <div className="flex flex-col items-center">
                        <div className="h-12 w-12 bg-blue-600 flex items-center justify-center mb-4">
                            <FaShieldHalved className="text-white text-2xl" />
                        </div>
                        <h1 className="text-2xl font-black text-white uppercase tracking-tighter">Sistem Kurulumu</h1>
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Yönetici Paneli Yapılandırması</p>
                    </div>
                </div>

                {error && (
                    <div className="mb-8 border-l-4 border-rose-600 bg-rose-600/10 p-4">
                        <p className="text-[11px] font-black text-rose-500 uppercase tracking-widest">{error}</p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Yönetici Kullanıcı Adı</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-600">
                                <FaUser size={14} />
                            </div>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                placeholder="ADMIN_USERNAME"
                                className="block w-full pl-11 pr-4 py-4 bg-white/5 border border-white/10 text-white text-xs font-bold placeholder-slate-700 focus:outline-none focus:border-blue-600 transition-colors uppercase tracking-widest"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">E-Posta Adresi</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-600">
                                <FaEnvelope size={14} />
                            </div>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                placeholder="ADMIN@WORKSPACE.COM"
                                className="block w-full pl-11 pr-4 py-4 bg-white/5 border border-white/10 text-white text-xs font-bold placeholder-slate-700 focus:outline-none focus:border-blue-600 transition-colors uppercase tracking-widest"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Güvenli Şifre</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-600">
                                <FaLock size={14} />
                            </div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                placeholder="••••••••"
                                className="block w-full pl-11 pr-4 py-4 bg-white/5 border border-white/10 text-white text-xs font-bold placeholder-slate-700 focus:outline-none focus:border-blue-600 transition-colors uppercase tracking-widest"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full flex items-center justify-between py-5 px-8 bg-blue-600 hover:bg-blue-500 text-white text-xs font-black uppercase tracking-[0.3em] transition-all disabled:opacity-50"
                    >
                        <span>{loading ? "YÜKLENİYOR..." : "SİSTEMİ BAŞLAT"}</span>
                        <FaArrowRight />
                    </button>
                </form>
            </div>
        </div>
    );
}