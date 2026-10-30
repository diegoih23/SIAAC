import { useCallback, useEffect, useState } from "react";
import { Radio, RefreshCw } from "lucide-react";
import EmptyState from "../../../components/ui/EmptyState";
import { useApi } from "../../../hooks/useApi";
import { useWebSocket } from "../../../hooks/useWebSocket";
import { endpoints } from "../../../api/endpoints";
import ZoneMonitorCard from "../components/ZoneMonitorCard";
import monitoringService from "../services/monitoringService";

export default function MonitoringPage() {
  const { items: zones, loading, reload } = useApi(endpoints.crops.zones, { params: { is_active: true } });
  const { items: cameras } = useApi(endpoints.monitoring.cameras);
  const [readings, setReadings] = useState({});
  const [feed, setFeed] = useState([]);
  const [connected, setConnected] = useState(false);

  const loadLatest = useCallback(async () => {
    try {
      const { data } = await monitoringService.latestReadings();
      const grouped = {};
      data.forEach((reading) => {
        grouped[reading.zone] = grouped[reading.zone] || {};
        grouped[reading.zone][reading.sensor_type] = reading;
      });
      setReadings(grouped);
    } catch {
      // El tablero sigue funcionando con los datos del WebSocket.
    }
  }, []);

  useEffect(() => {
    loadLatest();
  }, [loadLatest]);

  const handleMessage = useCallback((message) => {
    if (message.event === "sensor.reading") {
      const reading = message.payload;
      setReadings((prev) => ({
        ...prev,
        [reading.zone]: { ...(prev[reading.zone] || {}), [reading.sensor_type]: reading },
      }));
    }
    if (["detection.event", "device.registered"].includes(message.event)) {
      setFeed((prev) => [message.payload, ...prev].slice(0, 8));
    }
  }, []);

  const { status } = useWebSocket("/ws/monitoring/", { onMessage: handleMessage });
  useEffect(() => setConnected(status === "connected"), [status]);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Monitoreo en tiempo real</h1>
          <p>Lecturas de sensores y eventos de las cámaras conectadas.</p>
        </div>
        <div className="page-actions">
          <span className={`conn-pill ${connected ? "on" : "off"}`}><Radio size={14} /> {connected ? "Conectado" : "Desconectado"}</span>
          <button className="btn btn-ghost" onClick={() => { reload(); loadLatest(); }}><RefreshCw size={16} /> Actualizar</button>
        </div>
      </header>

      <div className="monitor-grid">
        {zones.map((zone) => (
          <ZoneMonitorCard
            key={zone.id}
            zone={zone}
            readings={readings[zone.id]}
            cameras={cameras.filter((camera) => camera.zone === zone.id)}
          />
        ))}
      </div>

      {zones.length === 0 && !loading && (
        <EmptyState title="No hay zonas activas" description="Registra una zona y asigna dispositivos para iniciar el monitoreo." />
      )}

      <section className="event-feed">
        <h3>Últimos eventos</h3>
        {feed.length === 0 ? <p className="muted">Sin eventos recientes.</p> : feed.map((item, index) => (
          <div className="feed-item" key={`${item.id || index}-${index}`}>
            <span className="pulse-dot" />
            <p><strong>{item.object_class || item.name || "Evento"}</strong> · zona {item.zone_name || item.zone || "—"}</p>
            <small>{item.detected_at ? new Date(item.detected_at).toLocaleTimeString("es-CO") : "ahora"}</small>
          </div>
        ))}
      </section>
    </div>
  );
}
