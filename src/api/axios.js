import axios from 'axios';

const api = axios.create({
    baseURL: process.env.API_BASE_URL || 'http://localhost:8000/api',
});

export default api;