import { create } from "zustand";
import { persist } from "zustand/middleware";
import api, { clearStoredTokens, getStoredToken, storeToken } from "../api/client";
import { endpoints } from "../api/endpoints";

export const SESSION_INACTIVITY_MS = 30 * 60 * 1000;

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      loading: false,
      error: null,
      authReady: false,
      rememberMe: true,

      login: async (username, password, remember = true) => {
        set({ loading: true, error: null });
        try {
          const { data } = await api.post(endpoints.auth.login, { username, password });
          if (data.two_factor_required) {
            set({ loading: false, rememberMe: remember });
            return { requiresTwoFactor: true, challengeId: data.challenge_id, detail: data.detail, expiresIn: data.expires_in };
          }
          saveSession(data, remember);
          set({ user: data.user, isAuthenticated: true, loading: false, rememberMe: remember });
          return { success: true };
        } catch (error) {
          set({
            loading: false,
            error: error.response?.data?.detail || "Credenciales inválidas.",
          });
          return { success: false };
        }
      },

      googleLogin: async (credential, remember = true) => {
        set({ loading: true, error: null });
        try {
          const { data } = await api.post(endpoints.auth.google, { credential });
          saveSession(data, remember);
          set({ user: data.user, isAuthenticated: true, loading: false, rememberMe: remember });
          return { success: true };
        } catch (error) {
          set({ loading: false, error: error.response?.data?.detail || "No se pudo iniciar sesión con Google." });
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
          saveSession(data, get().rememberMe);
          set({ user: data.user, isAuthenticated: true, loading: false });
          return { success: true };
        } catch (error) {
          set({ loading: false, error: error.response?.data?.detail || "Código no válido." });
          return { success: false, error: error.response?.data?.detail };
        }
      },

      fetchMe: async () => {
        if (!getStoredToken("siaac_access") && !getStoredToken("siaac_refresh")) {
          set({ authReady: true, user: null, isAuthenticated: false });
          return;
        }
        try {
          const { data } = await api.get(endpoints.auth.me);
          set({ user: data, isAuthenticated: true, authReady: true });
        } catch {
          get().logout();
          set({ authReady: true });
        }
      },

      logout: () => {
        const refresh = getStoredToken("siaac_refresh");
        api.post(endpoints.auth.logout, { refresh }).catch(() => {});
        clearStoredTokens();
        set({ user: null, isAuthenticated: false, authReady: true, rememberMe: true });
      },
    }),
    {
      name: "siaac-auth",
      partialize: (state) =>
        state.rememberMe
          ? { user: state.user, isAuthenticated: state.isAuthenticated, rememberMe: true }
          : {},
    }
  )
);

function saveSession(data, remember) {
  if (!remember) localStorage.removeItem("siaac-auth");
  storeToken("siaac_access", data.access, remember);
  storeToken("siaac_refresh", data.refresh, remember);
}
