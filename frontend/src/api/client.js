import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 20000,
});

let refreshing = null;

api.interceptors.request.use((config) => {
  const access = localStorage.getItem("siaac_access");
  if (access) config.headers.Authorization = `Bearer ${access}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const refresh = localStorage.getItem("siaac_refresh");

    if (error.response?.status === 401 && refresh && !original._retry) {
      original._retry = true;
      try {
        refreshing =
          refreshing ||
          axios.post(`${API_URL}/auth/token/refresh/`, { refresh }).then(({ data }) => {
            localStorage.setItem("siaac_access", data.access);
            if (data.refresh) localStorage.setItem("siaac_refresh", data.refresh);
            return data.access;
          });
        const access = await refreshing;
        refreshing = null;
        original.headers.Authorization = `Bearer ${access}`;
        return api(original);
      } catch (refreshError) {
        refreshing = null;
        localStorage.removeItem("siaac_access");
        localStorage.removeItem("siaac_refresh");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
