import api from "../../../api/client";
import { endpoints } from "../../../api/endpoints";

const reportsService = {
  dashboard: () => api.get(endpoints.reports.dashboard),
  list: (params) => api.get(endpoints.reports.reports, { params }),
  create: (payload) => api.post(endpoints.reports.reports, payload),
  regenerate: (id) => api.post(`${endpoints.reports.reports}${id}/regenerate/`),
  remove: (id) => api.delete(`${endpoints.reports.reports}${id}/`),
};

export default reportsService;
