import { useState, useEffect } from "react";
import {
    FaLayerGroup, FaTableColumns, FaFolderTree, FaListCheck,
    FaPeopleGroup, FaBell, FaCode, FaGear, FaArrowRightFromBracket,
    FaBars, FaMagnifyingGlass, FaPlus, FaBolt, FaFolderPlus,
    FaCircleCheck, FaXmark, FaMoon, FaSun, FaChevronRight, FaClock, FaShieldHalved
} from "react-icons/fa6";

export default function Dashboard() {
    const [tema, setTema] = useState(() => {
        if (typeof window !== "undefined") {
            const kaydedilen = localStorage.getItem("workspace-theme");
            if (kaydedilen) return kaydedilen;
            return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }
        return "dark";
    });
    const [sidebarAcik, setSidebarAcik] = useState(false);

    useEffect(() => {
        const el = window.document.documentElement;
        if (tema === "dark") {
            el.classList.add("dark");
            el.classList.remove("light");
        } else {
            el.classList.add("light");
            el.classList.remove("dark");
        }
        localStorage.setItem("workspace-theme", tema);
    }, [tema]);

    const temaDegistir = () => setTema(prev => (prev === "dark" ? "light" : "dark"));

    const istatistikler = [
        { etiket: "Sistem Verimliliği", deger: "%98.2", alt: "TurkishSystems Güvencesiyle", renk: "text-blue-600 dark:text-blue-400" },
        { etiket: "Aktif Projeler", deger: "12", alt: "4 Kritik Durumda", renk: "text-indigo-600 dark:text-indigo-400" },
        { etiket: "Tamamlanan Görevler", deger: "842", alt: "Bu Ay: +124", renk: "text-emerald-600 dark:text-emerald-400" },
        { etiket: "Güvenlik Skoru", deger: "A+", alt: "SSL & End-to-End Active", renk: "text-amber-600 dark:text-amber-400" }
    ];

    return (
        <div className="min-h-screen flex bg-[#f8fafc] dark:bg-[#0f172a] text-slate-900 dark:text-slate-100 font-sans transition-colors duration-500 overflow-hidden">
            {sidebarAcik && (
                <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-md z-[60] lg:hidden" onClick={() => setSidebarAcik(false)} />
            )}

            <aside className={`fixed inset-y-0 left-0 z-[70] w-72 bg-white dark:bg-[#1e293b] border-r border-slate-200 dark:border-white/5 transition-all duration-300 lg:translate-x-0 lg:static lg:h-screen ${sidebarAcik ? "translate-x-0" : "-translate-x-full"}`}>
                <div className="flex flex-col h-full">
                    <div className="p-8">
                        <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-slate-800 to-slate-900 dark:from-blue-600 dark:to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                                <FaShieldHalved className="text-white text-lg" />
                            </div>
                            <div>
                                <h2 className="font-bold text-xl tracking-tight">Workspace</h2>
                                <p className="text-[9px] text-slate-500 dark:text-blue-400 font-black uppercase tracking-[0.2em]">by TurkishSystems</p>
                            </div>
                        </div>
                    </div>

                    <nav className="flex-1 px-4 space-y-1 overflow-y-auto">
                        <MenuElemani icon={<FaTableColumns />} label="Merkezi Kontrol" active />
                        <MenuElemani icon={<FaFolderTree />} label="Operasyonlar" />
                        <MenuElemani icon={<FaListCheck />} label="İş Akışları" />
                        <MenuElemani icon={<FaPeopleGroup />} label="Organizasyon" />
                        <MenuElemani icon={<FaBell />} label="Sistem Uyarıları" badge="12" />

                        <div className="pt-8 pb-3 px-4 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Altyapı Yönetimi</div>
                        <MenuElemani icon={<FaCode />} label="Geliştirici Konsolu" />
                        <MenuElemani icon={<FaGear />} label="Sistem Ayarları" />
                    </nav>

                    <div className="p-6 mt-auto border-t border-slate-100 dark:border-white/5 bg-slate-50/50 dark:bg-[#1e293b]">
                        <button onClick={temaDegistir} className="flex items-center justify-between w-full p-3 bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-2xl mb-4 group hover:border-blue-500 transition-all">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-white/10">
                                    {tema === "dark" ? <FaMoon className="text-blue-400" /> : <FaSun className="text-amber-500" />}
                                </div>
                                <span className="text-xs font-bold">{tema === "dark" ? "Gece Modu" : "Gündüz Modu"}</span>
                            </div>
                            <div className={`w-8 h-4 rounded-full relative transition-colors ${tema === 'dark' ? 'bg-blue-600' : 'bg-slate-300'}`}>
                                <div className={`absolute top-1 w-2 h-2 bg-white rounded-full transition-all ${tema === 'dark' ? 'right-1' : 'left-1'}`} />
                            </div>
                        </button>

                        <button className="flex items-center gap-3 w-full px-4 py-3 text-slate-500 hover:text-rose-500 rounded-xl transition-all font-bold text-sm group">
                            <FaArrowRightFromBracket className="group-hover:-translate-x-1 transition-transform" />
                            <span>Güvenli Çıkış</span>
                        </button>
                    </div>
                </div>
            </aside>

            <main className="flex-1 h-screen overflow-y-auto relative scroll-smooth bg-[#f8fafc] dark:bg-[#0f172a]">
                <header className="sticky top-0 z-40 bg-white/70 dark:bg-[#0f172a]/70 backdrop-blur-xl border-b border-slate-200 dark:border-white/5 px-6 md:px-10 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-6">
                        <button onClick={() => setSidebarAcik(true)} className="lg:hidden p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl transition-colors">
                            <FaBars size={20} />
                        </button>
                        <div className="relative group hidden md:block">
                            <FaMagnifyingGlass className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                            <input type="text" placeholder="Workspace üzerinde ara..." className="w-80 bg-slate-100 dark:bg-white/5 border border-transparent focus:border-blue-500/50 rounded-2xl pl-11 pr-4 py-2.5 text-sm transition-all outline-none" />
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-lg text-[10px] font-black uppercase tracking-widest hidden sm:flex">
                            <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            Sunucu Erişimi Aktif
                        </div>
                        <div className="h-10 w-10 rounded-2xl border-2 border-white dark:border-slate-800 shadow-sm overflow-hidden flex items-center justify-center bg-slate-800 text-white font-bold text-xs">Eİ</div>
                    </div>
                </header>

                <div className="p-6 md:p-10 max-w-[1600px] mx-auto space-y-8">
                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight">Sistem Genel Bakış</h1>
                            <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">Hoş geldin Ekin İlter. TurkishSystems altyapısı sorunsuz çalışıyor.</p>
                        </div>
                        <div className="flex gap-2">
                            <button className="px-4 py-2 bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl text-xs font-bold hover:border-blue-500 transition-all">Veri Analizi</button>
                            <button className="px-4 py-2 bg-slate-900 dark:bg-blue-600 text-white rounded-xl text-xs font-bold hover:opacity-90 transition-all">Yeni Kayıt</button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {istatistikler.map((item, i) => (
                            <div key={i} className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 p-6 rounded-[2rem] shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                                <p className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">{item.etiket}</p>
                                <div className="mt-3 flex items-end justify-between">
                                    <h3 className={`text-3xl font-bold ${item.renk}`}>{item.deger}</h3>
                                    <span className="text-[10px] font-bold text-slate-400 mb-1">{item.alt}</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="grid lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-2 space-y-6">
                            <div className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 rounded-[2.5rem] shadow-sm overflow-hidden">
                                <div className="p-8 border-b border-slate-100 dark:border-white/5 flex items-center justify-between">
                                    <h3 className="font-bold text-lg">Aktif Operasyonlar</h3>
                                    <FaBolt className="text-blue-500" />
                                </div>
                                <div className="overflow-x-auto min-w-full">
                                    <table className="w-full text-left">
                                        <thead>
                                            <tr className="text-[11px] font-bold text-slate-400 uppercase tracking-widest bg-slate-50/50 dark:bg-white/[0.02]">
                                                <th className="px-8 py-4">Sistem Birimi</th>
                                                <th className="px-8 py-4">Durum</th>
                                                <th className="px-8 py-4 text-right">Yük Dağılımı</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                                            <ProjeSatiri isim="Workspace Core API" ekip="Backend Systems" durum="Optimal" yuzde={22} renk="bg-blue-600" />
                                            <ProjeSatiri isim="User Interface v4" ekip="Frontend Unit" durum="Güncelleniyor" yuzde={88} renk="bg-indigo-600" />
                                            <ProjeSatiri isim="Database Cluster" ekip="Infrastructure" durum="Stabil" yuzde={45} renk="bg-emerald-600" />
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 p-8 rounded-[2.5rem] shadow-sm">
                                <div className="flex items-center justify-between mb-8">
                                    <h3 className="font-bold text-lg">Sistem Günlüğü</h3>
                                    <button className="text-xs font-bold text-blue-500">Loglar</button>
                                </div>
                                <div className="space-y-6">
                                    <AktiviteElemani baslik="Yetkilendirme Başarılı" alt="Ekin İlter yönetici erişimi sağladı." zaman="Az önce" icon={<FaCircleCheck className="text-emerald-500" />} />
                                    <AktiviteElemani baslik="Yeni Dağıtım" alt="TurkishSystems Build #842 yayına alındı." zaman="1sa önce" icon={<FaBolt className="text-blue-500" />} />
                                    <AktiviteElemani baslik="Yedekleme Tamamlandı" alt="Günlük sistem yedeği AWS üzerinde depolandı." zaman="4sa önce" icon={<FaClock className="text-amber-500" />} />
                                </div>
                            </div>

                            <div className="bg-gradient-to-br from-slate-800 to-slate-950 p-8 rounded-[2.5rem] text-white shadow-xl shadow-slate-500/20 relative overflow-hidden group border border-white/5">
                                <div className="relative z-10">
                                    <h4 className="font-bold text-lg">TurkishSystems Enterprise</h4>
                                    <p className="text-slate-400 text-sm mt-2 font-medium opacity-90">Sınırsız operasyonel kapasite ve 7/24 teknik destek için lisansınızı güncelleyin.</p>
                                    <button className="mt-6 px-5 py-2.5 bg-blue-600 text-white rounded-xl text-xs font-black shadow-lg hover:scale-105 transition-transform">Detaylı Bilgi</button>
                                </div>
                                <FaShieldHalved className="absolute -right-6 -bottom-6 text-white/5 text-9xl -rotate-12 group-hover:rotate-0 transition-transform duration-700" />
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

function MenuElemani({ icon, label, active = false, badge = null }) {
    return (
        <a className={`flex items-center justify-between px-5 py-3.5 rounded-2xl cursor-pointer transition-all duration-300 group ${active ? "bg-slate-900 dark:bg-blue-600 text-white shadow-xl shadow-blue-600/30" : "text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-slate-200"}`}>
            <div className="flex items-center gap-4">
                <span className={`text-lg transition-transform group-hover:scale-110`}>{icon}</span>
                <span className="text-[13px] font-bold tracking-tight">{label}</span>
            </div>
            {badge && <span className="bg-blue-500 text-white text-[10px] font-black px-2 py-0.5 rounded-lg shadow-md">{badge}</span>}
        </a>
    );
}

function ProjeSatiri({ isim, ekip, durum, yuzde, renk }) {
    return (
        <tr className="group hover:bg-slate-50 dark:hover:bg-white/[0.01] transition-colors">
            <td className="px-8 py-6">
                <div className="flex flex-col">
                    <span className="font-bold text-sm">{isim}</span>
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-tighter mt-1">{ekip}</span>
                </div>
            </td>
            <td className="px-8 py-6">
                <span className="text-[10px] font-black px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-slate-500 uppercase tracking-widest">{durum}</span>
            </td>
            <td className="px-8 py-6">
                <div className="flex items-center justify-end gap-4">
                    <div className="w-24 h-2 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                        <div className={`h-full ${renk} shadow-sm`} style={{ width: `${yuzde}%` }} />
                    </div>
                    <span className="text-xs font-black text-slate-400 min-w-[30px]">{yuzde}%</span>
                </div>
            </td>
        </tr>
    );
}

function AktiviteElemani({ icon, baslik, alt, zaman }) {
    return (
        <div className="flex gap-4 group cursor-default">
            <div className="h-10 w-10 shrink-0 rounded-xl bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/10 flex items-center justify-center transition-colors group-hover:border-blue-500/50">
                {icon}
            </div>
            <div className="flex-1">
                <div className="flex items-center justify-between">
                    <h5 className="text-[13px] font-bold">{baslik}</h5>
                    <span className="text-[10px] font-medium text-slate-400">{zaman}</span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-1">{alt}</p>
            </div>
        </div>
    );
}