import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 20000,
});

let refreshing = null;

export const getStoredToken = (key) =>
  localStorage.getItem(key) || sessionStorage.getItem(key);

export const storeToken = (key, value, remember = true) => {
  const target = remember ? localStorage : sessionStorage;
  const other = remember ? sessionStorage : localStorage;
  target.setItem(key, value);
  other.removeItem(key);
};

export const clearStoredTokens = () => {
  ["siaac_access", "siaac_refresh"].forEach((key) => {
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
  });
};

api.interceptors.request.use((config) => {
  const access = getStoredToken("siaac_access");
  if (access) config.headers.Authorization = `Bearer ${access}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const refresh = getStoredToken("siaac_refresh");

    if (error.response?.status === 401 && refresh && !original._retry) {
      original._retry = true;
      try {
          refreshing =
          refreshing ||
          axios.post(`${API_URL}/auth/token/refresh/`, { refresh }).then(({ data }) => {
            const remember = Boolean(localStorage.getItem("siaac_refresh"));
            storeToken("siaac_access", data.access, remember);
            if (data.refresh) storeToken("siaac_refresh", data.refresh, remember);
            return data.access;
          });
        const access = await refreshing;
        refreshing = null;
        original.headers.Authorization = `Bearer ${access}`;
        return api(original);
      } catch (refreshError) {
        refreshing = null;
        clearStoredTokens();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
