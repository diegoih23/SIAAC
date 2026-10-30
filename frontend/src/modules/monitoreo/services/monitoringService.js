import api from "../../../api/client";
import { endpoints } from "../../../api/endpoints";

const monitoringService = {
  listCameras: (params) => api.get(endpoints.monitoring.cameras, { params }),
  createCamera: (payload) => api.post(endpoints.monitoring.cameras, payload),
  snapshot: (id) => api.post(`${endpoints.monitoring.cameras}${id}/snapshot/`),
  listReadings: (params) => api.get(endpoints.monitoring.readings, { params }),
  latestReadings: (zoneId) => api.get(endpoints.monitoring.latest, { params: { zone: zoneId } }),
};

export default monitoringService;
