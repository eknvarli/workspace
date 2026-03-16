import { create } from "zustand";

const getInitialUser = () => {
    try {
        const rawData = localStorage.getItem("user");
        return (rawData && rawData !== "undefined") ? JSON.parse(rawData) : null;
    } catch (error) {
        localStorage.removeItem("user");
        return null;
    }
};

const getInitialToken = () => {
    const rawData = localStorage.getItem("token");
    return (rawData && rawData !== "undefined") ? rawData : null;
};

const useAuthStore = create((set) => ({
    user: getInitialUser(),
    isAuthenticated: !!getInitialToken(),
    token: getInitialToken(),
    isSetupRequired: false,

    setSetupRequired: (required) => set({ isSetupRequired: required }),

    login: (userData, token) => {
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