import api from "../../../api/client";
import { endpoints } from "../../../api/endpoints";

const cropsService = {
  listCrops: (params) => api.get(endpoints.crops.crops, { params }),
  createCrop: (payload) => api.post(endpoints.crops.crops, payload),
  updateCrop: (id, payload) => api.patch(`${endpoints.crops.crops}${id}/`, payload),
  deleteCrop: (id) => api.delete(`${endpoints.crops.crops}${id}/`),
  listZones: (params) => api.get(endpoints.crops.zones, { params }),
  createZone: (payload) => api.post(endpoints.crops.zones, payload),
  updateZone: (id, payload) => api.patch(`${endpoints.crops.zones}${id}/`, payload),
  deleteZone: (id) => api.delete(`${endpoints.crops.zones}${id}/`),
};

export default cropsService;
