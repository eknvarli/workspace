import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FaUser, FaLock, FaArrowRight, FaEye, FaEyeSlash } from "react-icons/fa";
import useAuthStore from "../store/authStore";

export default function Login() {
    const navigate = useNavigate();
    const { login } = useAuthStore();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        if (username && password) {
            login({ username });
            navigate("/dashboard");
        } else {
            setError("Giriş bilgilerinizi kontrol edin.");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#0f172a] p-6 relative overflow-hidden">
            <div className="absolute top-[-10%] left-[-10%] w-72 h-72 bg-blue-600/20 rounded-full blur-[120px]" />
            <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-purple-600/10 rounded-full blur-[150px]" />

            <div className="max-w-md w-full z-10">
                <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl">
                    <div className="text-center mb-10">
                        <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2">
                            Workspace <span className="text-xs text-gray-300 font-light tracking-normal">by TurkishSystems</span>
                        </h1>
                        <p className="text-gray-400 font-medium">
                            Yet another project management system.
                        </p>
                    </div>

                    {error && (
                        <div className="mb-6 animate-pulse">
                            <div className="p-4 rounded-xl text-sm font-medium text-red-400 bg-red-500/10 border border-red-500/20">
                                {error}
                            </div>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider ml-1">
                                Kullanıcı Adı
                            </label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors group-focus-within:text-blue-500 text-gray-500">
                                    <FaUser size={18} />
                                </div>
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                    placeholder="Kullanıcı adınızı giriniz..."
                                    className="block w-full pl-11 pr-4 py-3.5 bg-white/5 border border-white/10 rounded-2xl text-white placeholder-gray-600 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:bg-white/10"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider ml-1">
                                Şifre
                            </label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors group-focus-within:text-blue-500 text-gray-500">
                                    <FaLock size={18} />
                                </div>
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    placeholder="••••••••"
                                    className="block w-full pl-11 pr-12 py-3.5 bg-white/5 border border-white/10 rounded-2xl text-white placeholder-gray-600 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:bg-white/10"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-500 hover:text-blue-400 transition-colors"
                                >
                                    {showPassword ? <FaEyeSlash size={20} /> : <FaEye size={20} />}
                                </button>
                            </div>
                        </div>

                        <div className="flex items-center justify-between py-1">
                            <label className="flex items-center space-x-3 cursor-pointer group">
                                <div className="relative">
                                    <input
                                        type="checkbox"
                                        checked={rememberMe}
                                        onChange={() => setRememberMe(!rememberMe)}
                                        className="sr-only"
                                    />
                                    <div className={`w-5 h-5 border-2 rounded-md transition-all ${rememberMe ? 'bg-blue-600 border-blue-600' : 'border-gray-600 bg-transparent'}`}>
                                        {rememberMe && <div className="text-white text-[10px] flex items-center justify-center h-full">✓</div>}
                                    </div>
                                </div>
                                <span className="text-sm text-gray-400 group-hover:text-gray-200 transition-colors">Beni hatırla</span>
                            </label>
                            <a href="#" className="text-sm font-medium text-blue-500 hover:text-blue-400">Şifremi Unuttum</a>
                        </div>

                        <button
                            type="submit"
                            className="w-full group relative flex items-center justify-center py-4 px-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-2xl shadow-lg shadow-blue-900/20 transition-all active:scale-[0.98]"
                        >
                            <span>Giriş Yap</span>
                            <FaArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
                        </button>
                    </form>

                    <div className="mt-8 text-center">
                        <p className="text-gray-400 text-sm">
                            Hesabınız yok mu?{" "}
                            <Link to="/register" className="text-white font-bold hover:underline decoration-blue-500 underline-offset-4">
                                Ücretsiz Kayıt Ol
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}