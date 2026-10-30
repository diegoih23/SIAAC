import { useCallback, useEffect, useState } from "react";
import api from "../api/client";

/** Hook de lectura con estados de carga/error y recarga manual. */
export function useApi(url, { params, enabled = true } = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    if (!url || !enabled) return;
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(url, { params });
      setData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo cargar la información.");
    } finally {
      setLoading(false);
    }
  }, [url, JSON.stringify(params), enabled]);

  useEffect(() => {
    load();
  }, [load]);

  const items = Array.isArray(data) ? data : data?.results || [];

  return { data, items, loading, error, reload: load };
}
