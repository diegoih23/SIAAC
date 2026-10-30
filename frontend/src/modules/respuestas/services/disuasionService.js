import api from "../../../api/client";
import { endpoints } from "../../../api/endpoints";

const disuasionService = {
  listRules: (params) => api.get(endpoints.disuasion.rules, { params }),
  createRule: (payload) => api.post(endpoints.disuasion.rules, payload),
  updateRule: (id, payload) => api.patch(`${endpoints.disuasion.rules}${id}/`, payload),
  activate: (id) => api.post(`${endpoints.disuasion.rules}${id}/activate/`),
  activations: (params) => api.get(endpoints.disuasion.activations, { params }),
};

export default disuasionService;
