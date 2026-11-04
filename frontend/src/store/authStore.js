import { create } from "zustand";
import { persist } from "zustand/middleware";
import api from "../api/client";
import { endpoints } from "../api/endpoints";

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      loading: false,
      error: null,

      login: async (username, password) => {
        set({ loading: true, error: null });
        try {
          const { data } = await api.post(endpoints.auth.login, { username, password });
          if (data.two_factor_required) {
            set({ loading: false });
            return { requiresTwoFactor: true, challengeId: data.challenge_id, detail: data.detail };
          }
          localStorage.setItem("siaac_access", data.access);
          localStorage.setItem("siaac_refresh", data.refresh);
          set({ user: data.user, isAuthenticated: true, loading: false });
          return { success: true };
        } catch (error) {
          set({
            loading: false,
            error: error.response?.data?.detail || "Credenciales inválidas.",
          });
          return { success: false };
        }
      },

      completeTwoFactor: async (challengeId, code) => {
        set({ loading: true, error: null });
        try {
          const { data } = await api.post(endpoints.auth.twoFactorVerify, {
            challenge_id: challengeId,
            code,
          });
          localStorage.setItem("siaac_access", data.access);
          localStorage.setItem("siaac_refresh", data.refresh);
          set({ user: data.user, isAuthenticated: true, loading: false });
          return { success: true };
        } catch (error) {
          set({ loading: false, error: error.response?.data?.detail || "Código no válido." });
          return { success: false, error: error.response?.data?.detail };
        }
      },

      fetchMe: async () => {
        try {
          const { data } = await api.get(endpoints.auth.me);
          set({ user: data, isAuthenticated: true });
        } catch {
          get().logout();
        }
      },

      logout: () => {
        const refresh = localStorage.getItem("siaac_refresh");
        api.post(endpoints.auth.logout, { refresh }).catch(() => {});
        localStorage.removeItem("siaac_access");
        localStorage.removeItem("siaac_refresh");
        set({ user: null, isAuthenticated: false });
      },
    }),
    {
      name: "siaac-auth",
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
