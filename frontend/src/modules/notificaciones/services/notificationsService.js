import api from "../../../api/client";
import { endpoints } from "../../../api/endpoints";

const notificationsService = {
  list: (params) => api.get(endpoints.notifications.list, { params }),
  unreadCount: () => api.get(endpoints.notifications.unreadCount),
  markRead: (id) => api.post(`${endpoints.notifications.list}${id}/mark_read/`),
  markAllRead: () => api.post(endpoints.notifications.markAllRead),
  preferences: () => api.get(endpoints.notifications.preferences),
  updatePreference: (id, payload) => api.patch(`${endpoints.notifications.preferences}${id}/`, payload),
};

export default notificationsService;
