import axios from 'axios';

const api = axios.create({
    baseURL: process.env.API_BASE_URL || 'http://localhost:8000/api',
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
        if (error.response && error.response.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("workspace-auth-storage");
        }
        return Promise.reject(error);
    }
);

export default api;