import { create } from "zustand";

const getInitialUser = () => {
    try {
        const rawData = localStorage.getItem("user");
        if (!rawData || rawData === "undefined" || rawData === "null") return null;
        return JSON.parse(rawData);
    } catch (error) {
        console.error("User parse error:", error);
        localStorage.removeItem("user");
        return null;
    }
};

const getInitialToken = () => {
    try {
        const rawData = localStorage.getItem("token");
        // Token genelde düz stringdir ama bazen tırnaklı kaydedilmiş olabilir
        if (!rawData || rawData === "undefined" || rawData === "null") return null;
        return rawData;
    } catch (error) {
        localStorage.removeItem("token");
        return null;
    }
};

const useAuthStore = create((set) => ({
    user: getInitialUser(),
    isAuthenticated: !!getInitialToken(),
    token: getInitialToken(),
    isSetupRequired: null,

    setSetupRequired: (required) => set({ isSetupRequired: required }),

    login: (userData, token) => {
        // Veri yazarken hata oluşmaması için kontrol
        if (!userData || !token) return;

        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("token", token);
        localStorage.setItem("workspace-auth-storage", "active");

        set({
            user: userData,
            isAuthenticated: true,
            token: token,
        });
    },

    logout: () => {
        localStorage.removeItem("user");
        localStorage.removeItem("token");
        localStorage.removeItem("workspace-auth-storage");
        set({
            user: null,
            isAuthenticated: false,
            token: null,
        });
    },
}));

export default useAuthStore;