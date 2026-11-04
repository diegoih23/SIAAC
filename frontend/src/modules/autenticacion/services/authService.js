import api from "../../../api/client";
import { endpoints } from "../../../api/endpoints";

const authService = {
  login: (payload) => api.post(endpoints.auth.login, payload),
  register: (payload) => api.post(endpoints.auth.register, payload),
  me: () => api.get(endpoints.auth.me),
  updateProfile: (payload) => api.patch(endpoints.auth.me, payload),
  changePassword: (payload) => api.post(endpoints.auth.changePassword, payload),
  requestPasswordReset: (email) => api.post(endpoints.auth.passwordResetRequest, { email }),
  verifyPasswordReset: (payload) => api.post(endpoints.auth.passwordResetVerify, payload),
  confirmPasswordReset: (payload) => api.post(endpoints.auth.passwordResetConfirm, payload),
  verifyTwoFactor: (payload) => api.post(endpoints.auth.twoFactorVerify, payload),
  toggleTwoFactor: (enabled) => api.post(endpoints.auth.twoFactorToggle, { enabled }),
  verifyEmail: (payload) => api.post(endpoints.auth.emailVerification, payload),
  resendEmailVerification: (email) => api.post(endpoints.auth.emailVerificationResend, { email }),
  logout: (refresh) => api.post(endpoints.auth.logout, { refresh }),
  sessions: () => api.get(endpoints.auth.sessions),
  revokeSession: (id) => api.post(`${endpoints.auth.sessions}${id}/revoke/`),
  users: () => api.get(endpoints.auth.users),
};

export default authService;
