import { useState, useEffect } from "react";
import {
    FaLayerGroup, FaTableColumns, FaFolderTree, FaListCheck,
    FaPeopleGroup, FaBell, FaCode, FaGear, FaArrowRightFromBracket,
    FaBars, FaMagnifyingGlass, FaPlus, FaBolt, FaFolderPlus,
    FaCircleCheck, FaXmark, FaMoon, FaSun, FaChevronRight, FaClock, FaShieldHalved,
    FaFileLines, FaUsersGear, FaUserPlus, FaUserCheck, FaUserXmark,
    FaDiagramProject, FaFileMedical, FaNoteSticky, FaUpload, FaDownload, FaTrash
} from "react-icons/fa6";
import ReactMarkdown from "react-markdown";

import { useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import api from "../api/axios";

export default function Dashboard() {
    const navigate = useNavigate();
    const { logout, user } = useAuthStore();
    const [tema, setTema] = useState(() => {
        if (typeof window !== "undefined") {
            const kaydedilen = localStorage.getItem("workspace-theme");
            if (kaydedilen) return kaydedilen;
            return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }
        return "dark";
    });
    const [sidebarAcik, setSidebarAcik] = useState(false);
    const [aktifSekme, setAktifSekme] = useState("overview");
    const [teamRequired, setTeamRequired] = useState(false);
    const [newTeamName, setNewTeamName] = useState("");
    const [teamError, setTeamError] = useState("");

    const [notes, setNotes] = useState([]);
    const [currentNote, setCurrentNote] = useState(null);
    const [isEditingNote, setIsEditingNote] = useState(false);
    const [isViewingNote, setIsViewingNote] = useState(false);

    const [customers, setCustomers] = useState([]);
    const [showCustomerModal, setShowCustomerModal] = useState(false);
    const [newCustomer, setNewCustomer] = useState({ name: "", company: "", email: "", phone: "" });

    const [stats, setStats] = useState({
        team_name: "",
        member_count: 0,
        total_todos: 0,
        completed_todos: 0,
        last_notes: [],
        active_projects: []
    });
    const [todos, setTodos] = useState([]);
    const [members, setMembers] = useState([]);
    const [showTodoModal, setShowTodoModal] = useState(false);
    const [newTodo, setNewTodo] = useState({ title: "", description: "", assigned_to: "", deadline: "" });

    const [projects, setProjects] = useState([]);
    const [currentProject, setCurrentProject] = useState(null);
    const [projectNotes, setProjectNotes] = useState([]);
    const [projectFiles, setProjectFiles] = useState([]);
    const [showProjectModal, setShowProjectModal] = useState(false);
    const [newProject, setNewProject] = useState({ name: "", description: "" });

    const [pendingUsers, setPendingUsers] = useState([]);
    const [adminLoading, setAdminLoading] = useState(false);
    const [adminMsg, setAdminMsg] = useState({ tip: "", metin: "" });

    const [searchTerm, setSearchTerm] = useState("");
    const [searchResults, setSearchResults] = useState({ notes: [], customers: [], projects: [] });
    const [isSearching, setIsSearching] = useState(false);
    const [showResults, setShowResults] = useState(false);

    useEffect(() => {
        checkTeam();
        fetchStats();
        if (user && user.is_staff) {
            fetchPendingUsers();
        }
    }, [user]);

    const checkTeam = async () => {
        try {
            const res = await api.get("/team/");
            setTeamRequired(false);
        } catch (err) {
            setTeamRequired(true);
        }
    };

    const handleCreateTeam = async (e) => {
        e.preventDefault();
        setTeamError("");
        try {
            await api.post("/team/", { name: newTeamName });
            setTeamRequired(false);
            window.location.reload();
        } catch (err) {
            setTeamError("Ekip oluşturulamadı. Lütfen tekrar deneyin.");
        }
    };

    const fetchStats = async () => {
        try {
            const res = await api.get("/stats/");
            setStats(res.data);
        } catch (err) { }
    };

    useEffect(() => {
        const delayDebounceFn = setTimeout(async () => {
            if (searchTerm.length > 1) {
                setIsSearching(true);
                try {
                    const res = await api.get(`/search-global/?q=${searchTerm}`);
                    setSearchResults(res.data);
                    setShowResults(true);
                } catch (err) { } finally {
                    setIsSearching(false);
                }
            } else {
                setSearchResults({ notes: [], customers: [], projects: [] });
                setShowResults(false);
            }
        }, 300);
        return () => clearTimeout(delayDebounceFn);
    }, [searchTerm]);

    const fetchNotes = async () => {
        try {
            const res = await api.get("/notes/");
            setNotes(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const saveNote = async () => {
        try {
            if (currentNote.id) {
                await api.put(`/notes/${currentNote.id}/`, currentNote);
            } else {
                await api.post("/notes/", currentNote);
            }
            setIsEditingNote(false);
            setIsViewingNote(false);
            setCurrentNote(null);
            fetchNotes();
        } catch (err) {
            console.error(err);
        }
    };

    const fetchCustomers = async () => {
        try {
            const res = await api.get("/customers/");
            setCustomers(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const addCustomer = async (e) => {
        e.preventDefault();
        try {
            await api.post("/customers/", newCustomer);
            setShowCustomerModal(false);
            fetchCustomers();
        } catch (err) {
            console.error(err);
        }
    };

    const fetchTodos = async () => {
        try {
            const res = await api.get("/todos/");
            setTodos(res.data);
        } catch (err) { }
    };

    const fetchMembers = async () => {
        try {
            const res = await api.get("/members/");
            setMembers(res.data);
        } catch (err) { }
    };

    const addTodo = async (e) => {
        e.preventDefault();
        try {
            await api.post("/todos/", newTodo);
            setShowTodoModal(false);
            setNewTodo({ title: "", description: "", assigned_to: "", deadline: "" });
            fetchTodos();
            fetchStats();
        } catch (err) { }
    };

    const fetchPendingUsers = async () => {
        setAdminLoading(true);
        try {
            const res = await api.get("/pending-users/");
            setPendingUsers(res.data);
        } catch (err) {
            setAdminMsg({ tip: "error", metin: "Kullanıcı listesi alınamadı." });
        } finally {
            setAdminLoading(false);
        }
    };

    const handleApproveAdmin = async (id) => {
        try {
            await api.post(`/approve-user/${id}/`);
            setAdminMsg({ tip: "success", metin: "Kullanıcı onaylandı." });
            fetchPendingUsers();
        } catch (err) {
            setAdminMsg({ tip: "error", metin: "İşlem başarısız." });
        }
    };

    const handleRejectAdmin = async (id) => {
        if (!window.confirm("Bu kullanıcıyı reddetmek istediğinize emin misiniz?")) return;
        try {
            await api.post(`/reject-user/${id}/`);
            setAdminMsg({ tip: "success", metin: "Kullanıcı reddedildi." });
            fetchPendingUsers();
        } catch (err) {
            setAdminMsg({ tip: "error", metin: "İşlem başarısız." });
        }
    };

    const fetchProjects = async () => {
        try {
            const res = await api.get("/projects/");
            setProjects(res.data);
        } catch (err) { }
    };

    const fetchProjectDetail = async (id) => {
        try {
            const res = await api.get(`/projects/${id}/`);
            setCurrentProject(res.data.project);
            setProjectNotes(res.data.notes);
            setProjectFiles(res.data.files);
        } catch (err) { }
    };

    const createProject = async (e) => {
        e.preventDefault();
        try {
            await api.post("/projects/", newProject);
            setShowProjectModal(false);
            setNewProject({ name: "", description: "" });
            fetchProjects();
            fetchStats();
        } catch (err) { }
    };

    const addProjectNote = async (projectId, content) => {
        try {
            await api.post(`/projects/${projectId}/notes/`, { content });
            fetchProjectDetail(projectId);
        } catch (err) { }
    };

    const deleteProjectNote = async (noteId, projectId) => {
        if (!window.confirm("Bu notu silmek istediğinize emin misiniz?")) return;
        try {
            await api.delete(`/project-notes/${noteId}/`);
            fetchProjectDetail(projectId);
        } catch (err) { }
    };

    const uploadProjectFile = async (projectId, file) => {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("name", file.name);
        try {
            await api.post(`/projects/${projectId}/files/`, formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            fetchProjectDetail(projectId);
        } catch (err) { }
    };

    useEffect(() => {
        if (aktifSekme !== "notes") {
            setIsEditingNote(false);
            setIsViewingNote(false);
            setCurrentNote(null);
        }
        if (aktifSekme === "notes") fetchNotes();
        if (aktifSekme === "customers") fetchCustomers();
        if (aktifSekme === "todos") {
            fetchTodos();
            fetchMembers();
        }
        if (aktifSekme === "overview") fetchStats();
        if (aktifSekme === "admin") fetchPendingUsers();
        if (aktifSekme === "projects") fetchProjects();
    }, [aktifSekme]);

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

    useEffect(() => {
        let interval;
        if (aktifSekme === "projects" && currentProject) {
            interval = setInterval(() => {
                fetchProjectDetail(currentProject.id);
            }, 5000);
        }
        return () => clearInterval(interval);
    }, [aktifSekme, currentProject?.id]);

    const temaDegistir = () => setTema(prev => (prev === "dark" ? "light" : "dark"));

    const istatistikler = [
        { etiket: "Sistem Verimliliği", deger: "%98.2", alt: "TurkishSystems Güvencesiyle", renk: "text-blue-600 dark:text-blue-400" },
        { etiket: "Aktif Projeler", deger: "12", alt: "4 Kritik Durumda", renk: "text-indigo-600 dark:text-indigo-400" },
        { etiket: "Tamamlanan Görevler", deger: "842", alt: "Bu Ay: +124", renk: "text-emerald-600 dark:text-emerald-400" },
        { etiket: "Güvenlik Skoru", deger: "A+", alt: "SSL & End-to-End Active", renk: "text-amber-600 dark:text-amber-400" }
    ];

    const handleLogout = async () => {
        try {
            await api.post("/logout/");
        } catch (error) {
            console.error("Logout error", error);
        } finally {
            logout();
            navigate("/login");
        }
    };

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
                        <MenuElemani icon={<FaTableColumns />} label="Merkezi Kontrol" active={aktifSekme === "overview"} onClick={() => setAktifSekme("overview")} />
                        <MenuElemani icon={<FaListCheck />} label="Todolar" active={aktifSekme === "todos"} onClick={() => setAktifSekme("todos")} />
                        <MenuElemani icon={<FaFileLines />} label="Ekip Notları" active={aktifSekme === "notes"} onClick={() => setAktifSekme("notes")} />
                        <MenuElemani icon={<FaUsersGear />} label="Potansiyel Müşteriler" active={aktifSekme === "customers"} onClick={() => setAktifSekme("customers")} />
                        <MenuElemani icon={<FaDiagramProject />} label="Proje Yönetimi" active={aktifSekme === "projects"} onClick={() => setAktifSekme("projects")} />
                        {user?.is_staff && (
                            <MenuElemani icon={<FaUserPlus />} label="Üye İstekleri" active={aktifSekme === "admin"} onClick={() => setAktifSekme("admin")} badge={pendingUsers.length > 0 ? pendingUsers.length.toString() : null} />
                        )}

                        <div className="pt-8 pb-3 px-4 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Altyapı Yönetimi</div>
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

                        <button onClick={handleLogout} className="flex items-center gap-3 w-full px-4 py-3 text-slate-500 hover:text-rose-500 rounded-xl transition-all font-bold text-sm group">
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
                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                placeholder="Workspace üzerinde ara..."
                                className="w-80 bg-slate-100 dark:bg-white/5 border border-transparent focus:border-blue-500/50 rounded-2xl pl-11 pr-4 py-2.5 text-sm transition-all outline-none"
                            />
                            {showResults && (
                                <div className="absolute top-full left-0 mt-2 w-96 bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/10 shadow-2xl rounded-2xl overflow-hidden z-[100] animate-in fade-in slide-in-from-top-2">
                                    <div className="max-h-[400px] overflow-y-auto p-2 space-y-4">
                                        {searchResults.projects.length > 0 && (
                                            <div>
                                                <p className="px-3 text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Projeler</p>
                                                {searchResults.projects.map(p => (
                                                    <div key={p.id} onClick={() => { setAktifSekme("projects"); fetchProjectDetail(p.id); setShowResults(false); setSearchTerm(""); }} className="p-3 hover:bg-slate-50 dark:hover:bg-white/5 rounded-xl cursor-pointer">
                                                        <p className="text-xs font-bold">{p.name}</p>
                                                        <p className="text-[10px] text-slate-500 line-clamp-1">{p.description}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                        {searchResults.notes.length > 0 && (
                                            <div>
                                                <p className="px-3 text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Notlar</p>
                                                {searchResults.notes.map(n => (
                                                    <div key={n.id} onClick={() => { setAktifSekme("notes"); setCurrentNote(n); setIsViewingNote(true); setShowResults(false); setSearchTerm(""); }} className="p-3 hover:bg-slate-50 dark:hover:bg-white/5 rounded-xl cursor-pointer">
                                                        <p className="text-xs font-bold">{n.title}</p>
                                                        <p className="text-[10px] text-slate-500 line-clamp-1">{n.content}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                        {searchResults.customers.length > 0 && (
                                            <div>
                                                <p className="px-3 text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Potansiyel Müşteriler</p>
                                                {searchResults.customers.map(c => (
                                                    <div key={c.id} onClick={() => { setAktifSekme("customers"); setShowResults(false); setSearchTerm(""); }} className="p-3 hover:bg-slate-50 dark:hover:bg-white/5 rounded-xl cursor-pointer">
                                                        <p className="text-xs font-bold">{c.name}</p>
                                                        <p className="text-[10px] text-slate-500">{c.company}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                        {searchResults.projects.length === 0 && searchResults.notes.length === 0 && searchResults.customers.length === 0 && !isSearching && (
                                            <p className="text-center py-6 text-xs text-slate-500 font-medium">Sonuç bulunamadı.</p>
                                        )}
                                        {isSearching && (
                                            <div className="flex items-center justify-center py-6">
                                                <div className="h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-lg text-[10px] font-black uppercase tracking-widest hidden sm:flex">
                            <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            Sunucu Erişimi Aktif
                        </div>
                        <div className="h-10 w-10 rounded-2xl border-2 border-white dark:border-slate-800 shadow-sm overflow-hidden flex items-center justify-center bg-slate-800 text-white font-bold text-xs">
                            {user?.username?.substring(0, 2).toUpperCase()}
                        </div>
                    </div>
                </header>

                <div className="p-6 md:p-10 max-w-[1600px] mx-auto space-y-8">
                    {aktifSekme === "overview" && (
                        <>
                            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                                <div>
                                    <h1 className="text-3xl font-bold tracking-tight">{stats.team_name || "Sistem Genel Bakış"}</h1>
                                    <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">Hoş geldin {user?.username}. Workspace altyapısı sorunsuz çalışıyor.</p>
                                </div>
                                <div className="flex gap-2">
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                                <div className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 p-6 rounded-[2rem] shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                                    <p className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Ekip Üyeleri</p>
                                    <div className="mt-3 flex items-end justify-between">
                                        <h3 className="text-3xl font-bold text-blue-600 dark:text-blue-400">{stats.member_count}</h3>
                                    </div>
                                </div>
                                <div className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 p-6 rounded-[2rem] shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                                    <p className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Bekleyen Todolar</p>
                                    <div className="mt-3 flex items-end justify-between">
                                        <h3 className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">{stats.total_todos - stats.completed_todos}</h3>
                                        <span className="text-[10px] font-bold text-slate-400 mb-1">Toplam: {stats.total_todos}</span>
                                    </div>
                                </div>
                                <div className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 p-6 rounded-[2rem] shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                                    <p className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Tamamlanan Görevler</p>
                                    <div className="mt-3 flex items-end justify-between">
                                        <h3 className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">{stats.completed_todos}</h3>
                                        <span className="text-[10px] font-bold text-slate-400 mb-1">Başarı Oranı: %{stats.total_todos > 0 ? ((stats.completed_todos / stats.total_todos) * 100).toFixed(1) : "0"}</span>
                                    </div>
                                </div>
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
                                                        <th className="px-8 py-4">Proje İsmi</th>
                                                        <th className="px-8 py-4">Durum</th>
                                                        <th className="px-8 py-4 text-right">Erişim</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                                                    {stats.active_projects.length === 0 ? (
                                                        <tr><td colSpan="3" className="px-8 py-6 text-center text-slate-400 text-sm">Aktif operasyon bulunmuyor.</td></tr>
                                                    ) : (
                                                        stats.active_projects.map(p => (
                                                            <tr key={p.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.01] transition-colors group">
                                                                <td className="px-8 py-6">
                                                                    <div className="flex flex-col">
                                                                        <span className="font-bold text-sm">{p.name}</span>
                                                                        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tight">Kurumsal Altyapı</span>
                                                                    </div>
                                                                </td>
                                                                <td className="px-8 py-6">
                                                                    <span className="px-3 py-1 bg-emerald-500/10 text-emerald-500 rounded-lg text-[10px] font-black uppercase tracking-widest">{p.status}</span>
                                                                </td>
                                                                <td className="px-8 py-6 text-right">
                                                                    <button onClick={() => { setCurrentProject(p); setAktifSekme("projects"); fetchProjectDetail(p.id); }} className="p-2 bg-slate-100 dark:bg-white/5 rounded-lg opacity-0 group-hover:opacity-100 transition-all text-slate-400 hover:text-blue-500"><FaChevronRight /></button>
                                                                </td>
                                                            </tr>
                                                        ))
                                                    )}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-6">
                                    <div className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 p-8 rounded-[2.5rem] shadow-sm">
                                        <div className="flex items-center justify-between mb-8">
                                            <h3 className="font-bold text-lg">Son Notlar</h3>
                                            <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                                        </div>
                                        <div className="space-y-6">
                                            {stats.last_notes.length === 0 ? (
                                                <p className="text-center text-slate-400 text-sm py-4">Notlar boş.</p>
                                            ) : (
                                                stats.last_notes.map(n => (
                                                    <AktiviteElemani key={n.id} baslik={n.title} alt={n.created_by_name} zaman={new Date(n.created_at).toLocaleTimeString("tr-TR", { hour: '2-digit', minute: '2-digit' })} icon={<FaNoteSticky className="text-blue-500" />} />
                                                ))
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}

                    {aktifSekme === "notes" && (
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <h2 className="text-3xl font-bold">Ekip Notları</h2>
                                {!isEditingNote && !isViewingNote && (
                                    <button onClick={() => { setCurrentNote({ title: "", content: "" }); setIsEditingNote(true); }} className="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold">Yeni Not</button>
                                )}
                            </div>

                            {isEditingNote ? (
                                <div className="bg-white dark:bg-[#1e293b] p-8 rounded-[2rem] border border-slate-200 dark:border-white/5 space-y-4">
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="font-bold text-lg">{currentNote.id ? "Notu Düzenle" : "Yeni Not"}</h3>
                                        <button onClick={() => { setIsEditingNote(false); if (!currentNote.id) setCurrentNote(null); }} className="p-2 hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl"><FaXmark /></button>
                                    </div>
                                    <input value={currentNote.title} onChange={(e) => setCurrentNote({ ...currentNote, title: e.target.value })} placeholder="Not Başlığı" className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl text-lg font-bold outline-none" />
                                    <textarea value={currentNote.content} onChange={(e) => setCurrentNote({ ...currentNote, content: e.target.value })} rows={10} placeholder="Markdown içeriği..." className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl font-mono outline-none" />
                                    <div className="flex gap-4">
                                        <button onClick={saveNote} className="px-6 py-2 bg-emerald-600 text-white rounded-xl font-bold text-sm uppercase">KAYDET</button>
                                        <button onClick={() => { setIsEditingNote(false); if (!currentNote.id) setCurrentNote(null); }} className="px-6 py-2 bg-slate-200 dark:bg-white/10 rounded-xl font-bold text-sm uppercase">VAZGEÇ</button>
                                    </div>
                                </div>
                            ) : isViewingNote ? (
                                <div className="bg-white dark:bg-[#1e293b] p-8 rounded-[2rem] border border-slate-200 dark:border-white/5 space-y-6 animate-in fade-in slide-in-from-bottom-4">
                                    <div className="flex items-center justify-between pb-6 border-b border-slate-100 dark:border-white/5">
                                        <div>
                                            <h3 className="font-black text-2xl uppercase">{currentNote.title}</h3>
                                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">{currentNote.created_by_name} • {new Date(currentNote.created_at).toLocaleString("tr-TR")}</p>
                                        </div>
                                        <div className="flex gap-2">
                                            <button onClick={() => setIsEditingNote(true)} className="px-5 py-2.5 bg-blue-600 text-white rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-blue-500 transition-all">DÜZENLE</button>
                                            <button onClick={() => { setIsViewingNote(false); setCurrentNote(null); }} className="p-2.5 bg-slate-100 dark:bg-white/5 rounded-xl hover:bg-slate-200 dark:hover:bg-white/10 transition-all"><FaXmark /></button>
                                        </div>
                                    </div>
                                    <div className="markdown-content max-w-none text-slate-600 dark:text-slate-300">
                                        <ReactMarkdown>{currentNote.content}</ReactMarkdown>
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {notes.length === 0 ? (
                                        <div className="bg-white dark:bg-[#1e293b] p-20 text-center rounded-[3rem] border border-dashed border-slate-200 dark:border-white/10">
                                            <FaNoteSticky className="mx-auto text-4xl text-slate-300 mb-4" />
                                            <p className="text-slate-500 font-medium">Henüz bir not paylaşılmamış.</p>
                                        </div>
                                    ) : (
                                        notes.map(note => (
                                            <div key={note.id} className="bg-white dark:bg-[#1e293b] p-6 rounded-3xl border border-slate-200 dark:border-white/5 flex items-center justify-between hover:scale-[1.01] transition-all cursor-pointer group shadow-sm" onClick={() => { setCurrentNote(note); setIsViewingNote(true); }}>
                                                <div className="flex items-center gap-6">
                                                    <div className="h-12 w-12 bg-slate-50 dark:bg-white/5 rounded-2xl flex items-center justify-center text-slate-400 group-hover:bg-blue-600 group-hover:text-white transition-all shadow-sm">
                                                        <FaNoteSticky />
                                                    </div>
                                                    <div>
                                                        <h3 className="font-bold text-lg group-hover:text-blue-500 transition-colors">{note.title}</h3>
                                                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.15em] mt-0.5">{note.created_by_name} • {new Date(note.created_at).toLocaleDateString("tr-TR")}</p>
                                                    </div>
                                                </div>
                                                <FaChevronRight className="text-slate-300 group-hover:text-blue-500 group-hover:translate-x-1 transition-all" />
                                            </div>
                                        ))
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    {aktifSekme === "customers" && (
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <h2 className="text-3xl font-bold">Potansiyel Müşteriler</h2>
                                <button onClick={() => setShowCustomerModal(true)} className="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold">Yeni Müşteri</button>
                            </div>

                            <div className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 rounded-[2.5rem] shadow-sm overflow-hidden">
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left">
                                        <thead>
                                            <tr className="text-[11px] font-bold text-slate-400 uppercase tracking-widest bg-slate-50/50 dark:bg-white/[0.02]">
                                                <th className="px-8 py-4">Müşteri</th>
                                                <th className="px-8 py-4">Şirket</th>
                                                <th className="px-8 py-4">İletişim</th>
                                                <th className="px-8 py-4">Durum</th>
                                                <th className="px-8 py-4 text-right">Kayıt</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                                            {customers.length === 0 ? (
                                                <tr><td colSpan="5" className="px-8 py-10 text-center text-slate-400 font-medium">Müşteri bulunmuyor.</td></tr>
                                            ) : (
                                                customers.map(c => (
                                                    <tr key={c.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.01] transition-colors">
                                                        <td className="px-8 py-6 font-bold">{c.name}</td>
                                                        <td className="px-8 py-6 text-slate-500 font-medium">{c.company}</td>
                                                        <td className="px-8 py-6">
                                                            <div className="flex flex-col gap-1">
                                                                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">{c.email}</span>
                                                                <span className="text-[10px] font-bold text-slate-400">{c.phone}</span>
                                                            </div>
                                                        </td>
                                                        <td className="px-8 py-6">
                                                            <span className="px-2 py-1 bg-blue-500/10 text-blue-500 rounded-lg text-[10px] font-black uppercase tracking-widest">{c.status}</span>
                                                        </td>
                                                        <td className="px-8 py-6 text-right">
                                                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{new Date(c.created_at).toLocaleDateString("tr-TR")}</span>
                                                        </td>
                                                    </tr>
                                                ))
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    )}

                    {aktifSekme === "todos" && (
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <h2 className="text-3xl font-bold">Todolar</h2>
                                <button onClick={() => { fetchMembers(); setShowTodoModal(true); }} className="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold">Yeni Görev</button>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {todos.map(todo => (
                                    <div key={todo.id} className="bg-white dark:bg-[#1e293b] p-6 rounded-[2rem] border border-slate-200 dark:border-white/5 shadow-sm space-y-4">
                                        <div className="flex items-start justify-between">
                                            <h3 className="font-bold text-lg">{todo.title}</h3>
                                            <span className={`px-2 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest ${todo.status === 'Tamamlandı' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'}`}>{todo.status}</span>
                                        </div>
                                        <p className="text-sm text-slate-500 line-clamp-2">{todo.description}</p>
                                        <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-white/5">
                                            <div className="flex items-center gap-2">
                                                <div className="h-6 w-6 rounded-full bg-slate-800 text-white text-[8px] flex items-center justify-center font-bold">
                                                    {todo.assigned_to_name?.substring(0, 2).toUpperCase() || "?"}
                                                </div>
                                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{todo.assigned_to_name || "Atanmadı"}</span>
                                            </div>
                                            {todo.deadline && (
                                                <div className="flex items-center gap-1 text-[10px] font-bold text-rose-500 uppercase tracking-tighter">
                                                    <FaClock />
                                                    {new Date(todo.deadline).toLocaleDateString("tr-TR")}
                                                </div>
                                            )}
                                        </div>
                                        {todo.status !== 'Tamamlandı' && (
                                            <button onClick={async () => {
                                                await api.put(`/todos/${todo.id}/`, { status: 'Tamamlandı' });
                                                fetchTodos();
                                                fetchStats();
                                            }} className="w-full py-2 bg-slate-100 dark:bg-white/5 hover:bg-emerald-500 hover:text-white transition-all rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-500">TAMAMLA</button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {aktifSekme === "admin" && (
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <h2 className="text-3xl font-bold">Üye İstekleri</h2>
                                <span className="bg-blue-500/10 text-blue-500 text-[10px] font-black px-3 py-1 rounded-lg uppercase tracking-widest">{pendingUsers.length} Beklemede</span>
                            </div>

                            {adminMsg.metin && (
                                <div className={`p-4 rounded-2xl border ${adminMsg.tip === "success" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-500" : "bg-rose-500/10 border-rose-500/20 text-rose-500"} text-sm font-bold animate-in fade-in slide-in-from-top-4`}>
                                    {adminMsg.metin}
                                </div>
                            )}

                            <div className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 rounded-[2.5rem] shadow-sm overflow-hidden">
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left">
                                        <thead>
                                            <tr className="text-[11px] font-bold text-slate-400 uppercase tracking-widest bg-slate-50/50 dark:bg-white/[0.02]">
                                                <th className="px-8 py-4">Kullanıcı</th>
                                                <th className="px-8 py-4">E-Posta</th>
                                                <th className="px-8 py-4">Kayıt Tarihi</th>
                                                <th className="px-8 py-4 text-right">İşlemler</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                                            {adminLoading ? (
                                                <tr><td colSpan="4" className="px-8 py-10 text-center text-slate-400 font-medium">Yükleniyor...</td></tr>
                                            ) : pendingUsers.length === 0 ? (
                                                <tr><td colSpan="4" className="px-8 py-10 text-center text-slate-400 font-medium">Onay bekleyen kullanıcı bulunmuyor.</td></tr>
                                            ) : (
                                                pendingUsers.map(u => (
                                                    <tr key={u.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.01] transition-colors">
                                                        <td className="px-8 py-6 font-bold">{u.username}</td>
                                                        <td className="px-8 py-6 text-slate-500">{u.email}</td>
                                                        <td className="px-8 py-6 text-slate-400 text-xs font-bold">{new Date(u.date_joined).toLocaleDateString("tr-TR")}</td>
                                                        <td className="px-8 py-6">
                                                            <div className="flex items-center justify-end gap-2">
                                                                <button onClick={() => handleApproveAdmin(u.id)} className="p-3 bg-emerald-500/10 text-emerald-500 rounded-xl hover:bg-emerald-500 hover:text-white transition-all"><FaUserCheck /></button>
                                                                <button onClick={() => handleRejectAdmin(u.id)} className="p-3 bg-rose-500/10 text-rose-500 rounded-xl hover:bg-rose-500 hover:text-white transition-all"><FaUserXmark /></button>
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
                    )}
                    {aktifSekme === "projects" && (
                        <div className="space-y-6">
                            {!currentProject ? (
                                <>
                                    <div className="flex items-center justify-between">
                                        <h2 className="text-3xl font-bold">Proje Yönetimi</h2>
                                        <button onClick={() => setShowProjectModal(true)} className="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold hover:bg-blue-500 transition-all flex items-center gap-2"><FaPlus /> Yeni Proje</button>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {projects.length === 0 ? (
                                            <div className="col-span-full py-20 text-center bg-white dark:bg-[#1e293b] rounded-[3rem] border border-dashed border-slate-200 dark:border-white/10">
                                                <FaDiagramProject className="mx-auto text-4xl text-slate-300 mb-4" />
                                                <p className="text-slate-500 font-medium">Henüz bir proje oluşturulmamış.</p>
                                            </div>
                                        ) : (
                                            projects.map(p => (
                                                <div key={p.id} onClick={() => fetchProjectDetail(p.id)} className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 p-8 rounded-[2.5rem] shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all cursor-pointer group">
                                                    <div className="flex items-start justify-between mb-6">
                                                        <div className="h-12 w-12 bg-blue-500/10 text-blue-500 rounded-2xl flex items-center justify-center text-xl group-hover:bg-blue-500 group-hover:text-white transition-all"><FaDiagramProject /></div>
                                                        <span className="px-3 py-1 bg-emerald-500/10 text-emerald-500 rounded-lg text-[10px] font-black uppercase tracking-widest">{p.status}</span>
                                                    </div>
                                                    <h3 className="text-xl font-bold mb-2 group-hover:text-blue-500 transition-colors uppercase">{p.name}</h3>
                                                    <p className="text-slate-500 dark:text-slate-400 text-sm line-clamp-2 mb-6">{p.description || "Açıklama girilmemiş."}</p>
                                                    <div className="pt-6 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
                                                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{new Date(p.created_at).toLocaleDateString("tr-TR")}</span>
                                                        <FaChevronRight className="text-slate-300 group-hover:text-blue-500 group-hover:translate-x-1 transition-all" />
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </>
                            ) : (
                                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                    <div className="flex items-center gap-4">
                                        <button onClick={() => setCurrentProject(null)} className="p-3 bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-2xl text-slate-400 hover:text-blue-500 transition-all"><FaPlus className="rotate-45" /></button>
                                        <div>
                                            <h2 className="text-3xl font-black uppercase">{currentProject.name}</h2>
                                            <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">{currentProject.description}</p>
                                        </div>
                                    </div>

                                    <div className="grid lg:grid-cols-3 gap-8">
                                        <div className="lg:col-span-2 space-y-6">
                                            <div className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 rounded-[2.5rem] p-8">
                                                <div className="flex items-center justify-between mb-8">
                                                    <h3 className="text-lg font-bold flex items-center gap-2"><FaNoteSticky className="text-blue-500" /> Proje Notları</h3>
                                                </div>
                                                <div className="space-y-4 mb-8">
                                                    {projectNotes.length === 0 ? (
                                                        <p className="text-center text-slate-400 py-10 italic">Henüz not eklenmemiş.</p>
                                                    ) : (
                                                        projectNotes.map(n => (
                                                            <div key={n.id} className="p-6 bg-slate-50 dark:bg-white/[0.02] rounded-3xl border border-slate-100 dark:border-white/5 group">
                                                                <div className="flex items-center justify-between">
                                                                    <p className="text-sm font-medium text-slate-700 dark:text-slate-300">{n.content}</p>
                                                                    {n.created_by === user.id && (
                                                                        <button onClick={() => deleteProjectNote(n.id, currentProject.id)} className="p-2 text-slate-400 hover:text-rose-500 opacity-0 group-hover:opacity-100 transition-all"><FaTrash size={12} /></button>
                                                                    )}
                                                                </div>
                                                                <div className="mt-4 flex items-center justify-between text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                                                    <span>{n.created_by_name}</span>
                                                                    <span>{new Date(n.created_at).toLocaleString("tr-TR")}</span>
                                                                </div>
                                                            </div>
                                                        ))
                                                    )}
                                                </div>
                                                <div className="flex gap-2">
                                                    <input id="new-project-note" placeholder="Hızlı bir not bırak..." className="flex-1 bg-slate-100 dark:bg-white/5 border border-transparent focus:border-blue-500/50 p-4 rounded-2xl outline-none transition-all" onKeyDown={e => {
                                                        if (e.key === 'Enter' && e.target.value.trim()) {
                                                            addProjectNote(currentProject.id, e.target.value);
                                                            e.target.value = '';
                                                        }
                                                    }} />
                                                    <button onClick={() => {
                                                        const el = document.getElementById('new-project-note');
                                                        if (el.value.trim()) {
                                                            addProjectNote(currentProject.id, el.value);
                                                            el.value = '';
                                                        }
                                                    }} className="p-4 bg-blue-600 text-white rounded-2xl hover:bg-blue-500 transition-all font-black text-xs uppercase"><FaPlus /></button>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="space-y-6">
                                            <div className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-white/5 rounded-[2.5rem] p-8">
                                                <div className="flex items-center justify-between mb-8">
                                                    <h3 className="text-lg font-bold flex items-center gap-2"><FaFolderTree className="text-blue-500" /> Dosyalar</h3>
                                                    <label className="p-2 bg-blue-500/10 text-blue-500 rounded-xl cursor-pointer hover:bg-blue-500 hover:text-white transition-all"><FaUpload /><input type="file" className="hidden" onChange={e => e.target.files[0] && uploadProjectFile(currentProject.id, e.target.files[0])} /></label>
                                                </div>
                                                <div className="space-y-3">
                                                    {projectFiles.length === 0 ? (
                                                        <p className="text-center text-slate-400 py-10 italic text-sm">Dosya yüklenmemiş.</p>
                                                    ) : (
                                                        projectFiles.map(f => (
                                                            <div key={f.id} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-white/[0.02] rounded-2xl border border-slate-100 dark:border-white/5 group">
                                                                <div className="flex items-center gap-3 overflow-hidden">
                                                                    <div className="p-2 bg-white dark:bg-white/5 rounded-lg text-blue-500"><FaFileLines /></div>
                                                                    <div className="flex flex-col overflow-hidden">
                                                                        <span className="text-xs font-bold truncate">{f.name}</span>
                                                                        <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tight">{f.uploaded_by_name}</span>
                                                                    </div>
                                                                </div>
                                                                <a href={`http://localhost:8000${f.file}`} target="_blank" rel="noreferrer" className="p-2 text-slate-400 hover:text-blue-500 transition-all"><FaDownload /></a>
                                                            </div>
                                                        ))
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </main>

            {teamRequired && (
                <div className="fixed inset-0 z-[100] bg-slate-900/90 backdrop-blur-xl flex items-center justify-center p-6">
                    <div className="bg-white dark:bg-[#1e293b] p-10 rounded-[3rem] shadow-2xl max-w-lg w-full text-center space-y-8 animate-in zoom-in-95">
                        <div className="h-16 w-16 bg-blue-600 rounded-3xl mx-auto flex items-center justify-center shadow-2xl shadow-blue-500/40">
                            <FaShieldHalved className="text-white text-3xl" />
                        </div>
                        <div>
                            <h2 className="text-3xl font-black mb-2">Ekip Kurulumu</h2>
                            <p className="text-slate-400 font-medium">Workspace'i kullanmak için bir ekip adı belirlemelisiniz.</p>
                        </div>
                        <form onSubmit={handleCreateTeam} className="space-y-4">
                            {teamError && <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-500 rounded-2xl text-sm font-bold">{teamError}</div>}
                            <input value={newTeamName} onChange={(e) => setNewTeamName(e.target.value)} placeholder="Örn: ABC Software" className="w-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-5 rounded-2xl text-center text-xl font-bold outline-none focus:ring-2 focus:ring-blue-500/30 transition-all" required />
                            <button type="submit" className="w-full py-5 bg-blue-600 hover:bg-blue-500 text-white font-black rounded-2xl shadow-xl shadow-blue-500/20 transition-all active:scale-95">BAŞLAT</button>
                        </form>
                    </div>
                </div>
            )}

            {showTodoModal && (
                <div className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md flex items-center justify-center p-6">
                    <div className="bg-white dark:bg-[#1e293b] p-10 rounded-[3rem] shadow-2xl max-w-lg w-full space-y-8">
                        <div className="flex items-center justify-between">
                            <h2 className="text-2xl font-black">Yeni Görev</h2>
                            <button onClick={() => setShowTodoModal(false)} className="p-2 hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl"><FaXmark /></button>
                        </div>
                        <form onSubmit={addTodo} className="space-y-4">
                            <input value={newTodo.title} onChange={e => setNewTodo({ ...newTodo, title: e.target.value })} placeholder="Görev Başlığı" className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl outline-none" required />
                            <textarea value={newTodo.description} onChange={e => setNewTodo({ ...newTodo, description: e.target.value })} placeholder="Açıklama" className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl outline-none" rows={3} />
                            <div className="grid grid-cols-2 gap-4">
                                <select value={newTodo.assigned_to} onChange={e => setNewTodo({ ...newTodo, assigned_to: e.target.value })} className="bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl outline-none text-xs font-bold uppercase tracking-widest">
                                    <option value="">Üye Ata</option>
                                    {members.map(m => <option key={m.id} value={m.id}>{m.username}</option>)}
                                </select>
                                <input type="datetime-local" value={newTodo.deadline} onChange={e => setNewTodo({ ...newTodo, deadline: e.target.value })} className="bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl outline-none text-xs" />
                            </div>
                            <button type="submit" className="w-full py-4 bg-blue-600 text-white font-bold rounded-2xl shadow-xl shadow-blue-500/20 transition-all">GÖREVİ EKLE</button>
                        </form>
                    </div>
                </div>
            )}

            {showProjectModal && (
                <div className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md flex items-center justify-center p-6">
                    <div className="bg-white dark:bg-[#1e293b] p-10 rounded-[3rem] shadow-2xl max-w-lg w-full space-y-8 animate-in zoom-in-95">
                        <div className="flex items-center justify-between">
                            <h2 className="text-2xl font-black">Yeni Proje</h2>
                            <button onClick={() => setShowProjectModal(false)} className="p-2 hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl"><FaXmark /></button>
                        </div>
                        <form onSubmit={createProject} className="space-y-4">
                            <input value={newProject.name} onChange={e => setNewProject({ ...newProject, name: e.target.value })} placeholder="Proje Adı" className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl outline-none" required />
                            <textarea value={newProject.description} onChange={e => setNewProject({ ...newProject, description: e.target.value })} placeholder="Proje Açıklaması" className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl outline-none" rows={4} />
                            <button type="submit" className="w-full py-4 bg-blue-600 text-white font-bold rounded-2xl shadow-xl shadow-blue-500/20 transition-all">PROJEYİ OLUŞTUR</button>
                        </form>
                    </div>
                </div>
            )}

            {showCustomerModal && (
                <div className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md flex items-center justify-center p-6">
                    <div className="bg-white dark:bg-[#1e293b] p-10 rounded-[3rem] shadow-2xl max-w-lg w-full space-y-8">
                        <div className="flex items-center justify-between">
                            <h2 className="text-2xl font-black">Yeni Müşteri</h2>
                            <button onClick={() => setShowCustomerModal(false)} className="p-2 hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl"><FaXmark /></button>
                        </div>
                        <form onSubmit={addCustomer} className="space-y-4">
                            <input value={newCustomer.name} onChange={e => setNewCustomer({ ...newCustomer, name: e.target.value })} placeholder="Ad Soyad" className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl outline-none" required />
                            <input value={newCustomer.company} onChange={e => setNewCustomer({ ...newCustomer, company: e.target.value })} placeholder="Şirket" className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl outline-none" required />
                            <input value={newCustomer.email} onChange={e => setNewCustomer({ ...newCustomer, email: e.target.value })} placeholder="E-Posta" className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl outline-none" required />
                            <input value={newCustomer.phone} onChange={e => setNewCustomer({ ...newCustomer, phone: e.target.value })} placeholder="Telefon" className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 p-4 rounded-xl outline-none" />
                            <button type="submit" className="w-full py-4 bg-blue-600 text-white font-bold transition-all">KAYDET</button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

function MenuElemani({ icon, label, active = false, badge = null, onClick }) {
    return (
        <a onClick={onClick} className={`flex items-center justify-between px-4 py-3 cursor-pointer transition-colors border-l-4 ${active ? "bg-blue-600/10 border-blue-600 text-blue-500" : "border-transparent text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-700 dark:hover:text-slate-200"}`}>
            <div className="flex items-center gap-3">
                <span className="text-base">{icon}</span>
                <span className="text-xs font-bold uppercase tracking-widest">{label}</span>
            </div>
            {badge && <span className="bg-blue-600 text-white text-[9px] font-black px-1.5 py-0.5">{badge}</span>}
        </a>
    );
}

function ProjeSatiri({ isim, ekip, durum, yuzde, renk }) {
    return (
        <tr className="border-b border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/[0.01]">
            <td className="px-6 py-4">
                <div className="flex flex-col">
                    <span className="font-bold text-xs">{isim}</span>
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">{ekip}</span>
                </div>
            </td>
            <td className="px-6 py-4">
                <span className="text-[9px] font-black px-2 py-1 border border-slate-200 dark:border-white/10 text-slate-500 uppercase tracking-widest">{durum}</span>
            </td>
            <td className="px-6 py-4">
                <div className="flex items-center justify-end gap-3">
                    <div className="w-20 h-1 bg-slate-100 dark:bg-white/5 overflow-hidden">
                        <div className={`h-full ${renk}`} style={{ width: `${yuzde}%` }} />
                    </div>
                    <span className="text-[10px] font-black text-slate-400">{yuzde}%</span>
                </div>
            </td>
        </tr>
    );
}

function AktiviteElemani({ icon, baslik, alt, zaman }) {
    return (
        <div className="flex gap-4 group cursor-default">
            <div className="h-8 w-8 shrink-0 bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/10 flex items-center justify-center">
                {icon}
            </div>
            <div className="flex-1">
                <div className="flex items-center justify-between">
                    <h5 className="text-xs font-bold uppercase tracking-tight">{baslik}</h5>
                    <span className="text-[9px] font-medium text-slate-400 uppercase">{zaman}</span>
                </div>
                <p className="text-[10px] text-slate-500 font-bold mt-0.5 uppercase tracking-tighter">{alt}</p>
            </div>
        </div>
    );
}
