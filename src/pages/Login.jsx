import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FaUser, FaLock, FaArrowRight, FaEye, FaEyeSlash } from "react-icons/fa";
import useAuthStore from "../store/authStore";
import api from "../api/axios";

export default function Login() {
    const navigate = useNavigate();
    const { login } = useAuthStore();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        try {
            const response = await api.post("/login/", { username, password });
            login(response.data.user, response.data.token);
            navigate("/dashboard");
        } catch (err) {
            if (err.response && err.response.data && err.response.data.error) {
                setError(err.response.data.error);
            } else {
                setError("Giriş başarısız. Lütfen bilgilerinizi kontrol edin.");
            }
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#020617] p-6">
            <div className="max-w-md w-full border border-white/5 bg-[#0a0f1e] p-10 shadow-2xl">
                <div className="mb-12 border-b border-white/5 pb-8">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="h-8 w-8 bg-blue-600 flex items-center justify-center font-black text-white">W</div>
                        <span className="text-sm font-black text-white tracking-widest uppercase">Workspace Portal</span>
                    </div>
                    <h1 className="text-2xl font-black text-white uppercase tracking-tighter">Sistem Girişi</h1>
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mt-2">Proje Yönetim Sistemi</p>
                </div>

                {error && (
                    <div className="mb-8 border-l-4 border-rose-600 bg-rose-600/10 p-4">
                        <p className="text-[11px] font-black text-rose-500 uppercase tracking-widest">{error}</p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Kullanıcı Adı</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-600">
                                <FaUser size={14} />
                            </div>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                placeholder="USERNAME"
                                className="block w-full pl-11 pr-4 py-4 bg-white/5 border border-white/10 text-white text-xs font-bold placeholder-slate-700 focus:outline-none focus:border-blue-600 transition-colors uppercase tracking-widest"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Şifre</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-600">
                                <FaLock size={14} />
                            </div>
                            <input
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                placeholder="••••••••"
                                className="block w-full pl-11 pr-12 py-4 bg-white/5 border border-white/10 text-white text-xs font-bold placeholder-slate-700 focus:outline-none focus:border-blue-600 transition-colors uppercase tracking-widest"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-600 hover:text-white transition-colors"
                            >
                                {showPassword ? <FaEyeSlash size={16} /> : <FaEye size={16} />}
                            </button>
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="w-full flex items-center justify-between py-5 px-8 bg-blue-600 hover:bg-blue-500 text-white text-xs font-black uppercase tracking-[0.3em] transition-all"
                    >
                        <span>Sisteme Giriş</span>
                        <FaArrowRight />
                    </button>
                </form>

                <div className="mt-12 pt-8 border-t border-white/5 text-center">
                    <p className="text-slate-500 text-[10px] font-black uppercase tracking-widest">
                        Hesabınız yok mu?{" "}
                        <Link to="/register" className="text-white hover:text-blue-500 transition-colors border-b border-white/20 pb-0.5 ml-2">
                            YENİ KAYIT
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}