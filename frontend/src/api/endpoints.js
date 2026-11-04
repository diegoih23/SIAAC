/** Mapa central de endpoints por módulo (evita URLs dispersas). */
export const endpoints = {
  auth: {
    login: "/auth/token/",
    refresh: "/auth/token/refresh/",
    register: "/auth/register/",
    me: "/auth/me/",
    changePassword: "/auth/change-password/",
    logout: "/auth/logout/",
    passwordResetRequest: "/auth/password-reset/request/",
    passwordResetVerify: "/auth/password-reset/verify/",
    passwordResetConfirm: "/auth/password-reset/confirm/",
    twoFactorVerify: "/auth/two-factor/verify/",
    twoFactorToggle: "/auth/two-factor/toggle/",
    emailVerification: "/auth/email-verification/verify/",
    emailVerificationResend: "/auth/email-verification/resend/",
    users: "/auth/users/",
    sessions: "/auth/sessions/",
  },
  crops: {
    crops: "/crops/crops/",
    zones: "/crops/zones/",
  },
  monitoring: {
    cameras: "/monitoring/cameras/",
    readings: "/monitoring/readings/",
    latest: "/monitoring/readings/latest/",
    ingest: "/monitoring/readings/ingest/",
  },
  reports: {
    reports: "/reports/",
    dashboard: "/reports/dashboard/summary/",
  },
  disuasion: {
    rules: "/disuasion/rules/",
    activations: "/disuasion/activations/",
  },
  notifications: {
    list: "/notifications/",
    unreadCount: "/notifications/unread_count/",
    markAllRead: "/notifications/mark_all_read/",
    preferences: "/notifications/preferences/",
  },
  detection: {
    devices: "/detection/devices/",
    models: "/detection/models/",
    events: "/detection/events/",
    ingest: "/detection/events/ingest/",
    statistics: "/detection/events/statistics/",
  },
};
