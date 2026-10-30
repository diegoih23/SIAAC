import api from "../../../api/client";
import { endpoints } from "../../../api/endpoints";

const detectionService = {
  listEvents: (params) => api.get(endpoints.detection.events, { params }),
  getEvent: (id) => api.get(`${endpoints.detection.events}${id}/`),
  reviewEvent: (id, payload) => api.post(`${endpoints.detection.events}${id}/review/`, payload),
  statistics: () => api.get(endpoints.detection.statistics),
  listDevices: (params) => api.get(endpoints.detection.devices, { params }),
  createDevice: (payload) => api.post(endpoints.detection.devices, payload),
  heartbeat: (id, payload) => api.post(`${endpoints.detection.devices}${id}/heartbeat/`, payload),
  listModels: () => api.get(endpoints.detection.models),
};

export default detectionService;
