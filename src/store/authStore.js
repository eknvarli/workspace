import { create } from "zustand";

const useAuthStore = create((set) => ({
    user: JSON.parse(localStorage.getItem("user")) || null,
    isAuthenticated: !!localStorage.getItem("token"),
    token: localStorage.getItem("token") || null,
    isSetupRequired: false,

    setSetupRequired: (required) => set({ isSetupRequired: required }),

    login: (userData, token) => {
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("token", token);
        set({
            user: userData,
            isAuthenticated: true,
            token: token,
        });
    },

    logout: () => {
        localStorage.removeItem("user");
        localStorage.removeItem("token");
        set({
            user: null,
            isAuthenticated: false,
            token: null,
        });
    },
}));

export default useAuthStore;