import axios from 'axios';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        const url = error.config?.url || "";
        const publicEndpoints = ["/setup-status/", "/setup/", "/login/", "/register/"];
        const isPublic = publicEndpoints.some(e => url.includes(e));
        if (error.response && error.response.status === 401 && !isPublic) {
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            localStorage.removeItem("workspace-auth-storage");
        }
        return Promise.reject(error);
    }
);

export default api;