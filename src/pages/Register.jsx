import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FaUser, FaLock, FaEnvelope, FaArrowRight, FaEye, FaEyeSlash } from "react-icons/fa";
import api from "../api/axios";

export default function Register() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        if (!username || !email || !password || !confirmPassword) {
            setError("Lütfen tüm alanları doldurun.");
            return;
        }
        if (password !== confirmPassword) {
            setError("Şifreler birbiriyle uyuşmuyor.");
            return;
        }

        try {
            await api.post("/register/", { username, email, password });
            setSuccess("Kayıt başarılı! Lütfen yöneticinin hesabınızı onaylamasını bekleyin.");
            setUsername("");
            setEmail("");
            setPassword("");
            setConfirmPassword("");
        } catch (err) {
            if (err.response && err.response.data) {
                const data = err.response.data;
                const firstError = Object.values(data)[0];
                setError(Array.isArray(firstError) ? firstError[0] : "Kayıt sırasında bir hata oluştu.");
            } else {
                setError("Sunucuya bağlanılamadı.");
            }
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#020617] p-6">
            <div className="max-w-md w-full border border-white/5 bg-[#0a0f1e] p-10 shadow-2xl">
                <div className="mb-10 border-b border-white/5 pb-8">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="h-8 w-8 bg-blue-600 flex items-center justify-center font-black text-white">W</div>
                        <span className="text-sm font-black text-white tracking-widest uppercase">Workspace Portal</span>
                    </div>
                    <h1 className="text-2xl font-black text-white uppercase tracking-tighter">Yeni Kayıt</h1>
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mt-2">Ekibin Bir Parçası Olun</p>
                </div>

                {success && (
                    <div className="mb-8 border-l-4 border-emerald-600 bg-emerald-600/10 p-4">
                        <p className="text-[11px] font-black text-emerald-500 uppercase tracking-widest leading-relaxed">{success}</p>
                    </div>
                )}

                {error && (
                    <div className="mb-8 border-l-4 border-rose-600 bg-rose-600/10 p-4">
                        <p className="text-[11px] font-black text-rose-500 uppercase tracking-widest">{error}</p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-1.5">
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
                                className="block w-full pl-11 pr-4 py-3.5 bg-white/5 border border-white/10 text-white text-xs font-bold focus:outline-none focus:border-blue-600 transition-colors uppercase tracking-widest"
                            />
                        </div>
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">E-Posta</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-600">
                                <FaEnvelope size={14} />
                            </div>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                placeholder="EMAIL@ADDRESS.COM"
                                className="block w-full pl-11 pr-4 py-3.5 bg-white/5 border border-white/10 text-white text-xs font-bold focus:outline-none focus:border-blue-600 transition-colors uppercase tracking-widest"
                            />
                        </div>
                    </div>

                    <div className="space-y-1.5">
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
                                className="block w-full pl-11 pr-12 py-3.5 bg-white/5 border border-white/10 text-white text-xs font-bold focus:outline-none focus:border-blue-600 transition-colors uppercase tracking-widest"
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

                    <div className="space-y-1.5">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Şifre Tekrar</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-600">
                                <FaLock size={14} />
                            </div>
                            <input
                                type={showPassword ? "text" : "password"}
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                placeholder="••••••••"
                                className="block w-full pl-11 pr-4 py-3.5 bg-white/5 border border-white/10 text-white text-xs font-bold focus:outline-none focus:border-blue-600 transition-colors uppercase tracking-widest"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="w-full flex items-center justify-between py-5 px-8 mt-6 bg-blue-600 hover:bg-blue-500 text-white text-xs font-black uppercase tracking-[0.3em] transition-all"
                    >
                        <span>Hesap Oluştur</span>
                        <FaArrowRight />
                    </button>
                </form>

                <div className="mt-12 pt-8 border-t border-white/5 text-center">
                    <p className="text-slate-500 text-[10px] font-black uppercase tracking-widest">
                        Zaten hesabınız var mı?{" "}
                        <Link to="/login" className="text-white hover:text-blue-500 transition-colors border-b border-white/20 pb-0.5 ml-2">
                            GİRİŞ YAP
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}