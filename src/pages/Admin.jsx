import { useState, useEffect } from "react";
import { FaUserCheck, FaUserXmark, FaShieldHalved, FaUsers, FaArrowLeft } from "react-icons/fa6";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

export default function Admin() {
    const navigate = useNavigate();
    const [pendingUsers, setPendingUsers] = useState([]);
    const [yukleniyor, setYukleniyor] = useState(true);
    const [mesaj, setMesaj] = useState({ tip: "", metin: "" });

    useEffect(() => {
        fetchPendingUsers();
    }, []);

    const fetchPendingUsers = async () => {
        try {
            const res = await api.get("/pending-users/");
            setPendingUsers(res.data);
        } catch (err) {
            setMesaj({ tip: "error", metin: "Kullanıcı listesi alınamadı." });
        } finally {
            setYukleniyor(false);
        }
    };

    const handleApprove = async (id) => {
        try {
            await api.post(`/approve-user/${id}/`);
            setMesaj({ tip: "success", metin: "Kullanıcı başarıyla onaylandı." });
            fetchPendingUsers();
        } catch (err) {
            setMesaj({ tip: "error", metin: "Kullanıcı onaylanamadı." });
        }
    };

    const handleReject = async (id) => {
        if (!window.confirm("Bu kullanıcıyı reddetmek istediğinize emin misiniz?")) return;
        try {
            await api.post(`/reject-user/${id}/`);
            setMesaj({ tip: "success", metin: "Kullanıcı reddedildi." });
            fetchPendingUsers();
        } catch (err) {
            setMesaj({ tip: "error", metin: "İşlem başarısız." });
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-[#020617] p-6 lg:p-12">
            <div className="max-w-5xl mx-auto space-y-10">
                <div className="flex items-center justify-between border-b border-slate-200 dark:border-white/5 pb-8">
                    <div className="flex items-center gap-6">
                        <button onClick={() => navigate("/dashboard")} className="p-4 bg-white dark:bg-[#0a0f1e] border border-slate-200 dark:border-white/10 hover:border-blue-500 transition-colors text-slate-500">
                            <FaArrowLeft />
                        </button>
                        <div>
                            <h1 className="text-2xl font-black text-slate-900 dark:text-white uppercase tracking-tight">Yönetici Paneli</h1>
                            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Sistem Üyelik Onay ve Denetim Merkezi</p>
                        </div>
                    </div>
                    <div className="h-12 w-12 bg-blue-600 flex items-center justify-center">
                        <FaShieldHalved className="text-white text-xl" />
                    </div>
                </div>

                {mesaj.metin && (
                    <div className={`p-4 border-l-4 ${mesaj.tip === "success" ? "bg-emerald-500/10 border-emerald-500 text-emerald-500" : "bg-rose-500/10 border-rose-500 text-rose-500"} text-[11px] font-black uppercase tracking-widest`}>
                        {mesaj.metin}
                    </div>
                )}

                <div className="bg-white dark:bg-[#0a0f1e] border border-slate-200 dark:border-white/5 shadow-sm">
                    <div className="p-6 border-b border-slate-100 dark:border-white/5 flex items-center justify-between bg-slate-50/50 dark:bg-white/[0.01]">
                        <div className="flex items-center gap-3">
                            <FaUsers className="text-blue-500" />
                            <h3 className="text-[11px] font-black uppercase tracking-[0.2em]">Onay Bekleyen Kullanıcılar</h3>
                        </div>
                        <span className="bg-blue-600 text-white text-[9px] font-black px-3 py-1 uppercase tracking-widest">{pendingUsers.length} BEKLEMEDE</span>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="text-[10px] font-bold text-slate-400 uppercase tracking-widest border-b border-slate-100 dark:border-white/5">
                                    <th className="px-8 py-4">Kimlik</th>
                                    <th className="px-8 py-4">E-Posta Adresi</th>
                                    <th className="px-8 py-4">Başvuru Tarihi</th>
                                    <th className="px-8 py-4 text-right">Eylem</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                                {yukleniyor ? (
                                    <tr>
                                        <td colSpan="4" className="px-8 py-12 text-center text-slate-400 text-[10px] font-black uppercase tracking-widest">Veri Yükleniyor...</td>
                                    </tr>
                                ) : pendingUsers.length === 0 ? (
                                    <tr>
                                        <td colSpan="4" className="px-8 py-12 text-center text-slate-400 text-[10px] font-black uppercase tracking-widest">Onay Bekleyen Kayıt Bulunmuyor</td>
                                    </tr>
                                ) : (
                                    pendingUsers.map(u => (
                                        <tr key={u.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.01] transition-colors group">
                                            <td className="px-8 py-6">
                                                <div className="flex items-center gap-4">
                                                    <div className="h-10 w-10 bg-slate-900 dark:bg-blue-600 flex items-center justify-center text-white font-black text-xs">
                                                        {u.username.substring(0, 2).toUpperCase()}
                                                    </div>
                                                    <span className="font-bold text-xs uppercase tracking-tight">{u.username}</span>
                                                </div>
                                            </td>
                                            <td className="px-8 py-6 text-slate-500 dark:text-slate-400 text-[11px] font-bold">{u.email}</td>
                                            <td className="px-8 py-6 text-slate-400 text-[10px] font-black uppercase">{new Date(u.date_joined).toLocaleDateString("tr-TR")}</td>
                                            <td className="px-8 py-6">
                                                <div className="flex items-center justify-end gap-1">
                                                    <button onClick={() => handleApprove(u.id)} className="px-4 py-2 border border-emerald-500/20 text-emerald-500 text-[9px] font-black uppercase tracking-widest hover:bg-emerald-600 hover:text-white transition-all">
                                                        ONAYLA
                                                    </button>
                                                    <button onClick={() => handleReject(u.id)} className="px-4 py-2 border border-rose-500/20 text-rose-500 text-[9px] font-black uppercase tracking-widest hover:bg-rose-600 hover:text-white transition-all">
                                                        REDDET
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}