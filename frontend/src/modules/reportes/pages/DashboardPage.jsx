import { Link } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Bell, Camera, Cpu, Leaf, Map, Siren } from "lucide-react";
import Card from "../../../components/ui/Card";
import StatCard from "../../../components/ui/StatCard";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";

export default function DashboardPage() {
  const { data: summary, loading } = useApi(endpoints.reports.dashboard);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Tablero general</h1>
          <p>Resumen operativo de las últimas 24 horas.</p>
        </div>
        <Link to="/monitoring" className="btn btn-primary">Ver monitoreo en vivo</Link>
      </header>

      {loading && <p className="muted">Cargando indicadores…</p>}

      <div className="stats-grid">
        <StatCard label="Zonas activas" value={summary?.zones?.active ?? "—"} hint={`${summary?.zones?.total ?? 0} zonas registradas`} icon={Map} />
        <StatCard label="Cultivos" value={summary?.crops ?? "—"} hint="Especies en seguimiento" accent="lime" icon={Leaf} />
        <StatCard label="Detecciones 24 h" value={summary?.detections_24h ?? "—"} hint="Eventos generados por YOLO" accent="orange" icon={Camera} />
        <StatCard label="Dispositivos en línea" value={`${summary?.devices?.online ?? 0}/${summary?.devices?.total ?? 0}`} hint="ESP32 · Raspberry Pi · cámaras" accent="blue" icon={Cpu} />
        <StatCard label="Activaciones disuasivas" value={summary?.disuasions_24h ?? "—"} hint="Sirenas y luces" accent="red" icon={Siren} />
        <StatCard label="Sin leer" value={summary?.unread_notifications ?? "—"} hint="Notificaciones pendientes" accent="slate" icon={Bell} />
      </div>

      <div className="grid-2">
        <Card title="Clases detectadas (24 h)" subtitle="Top 5 de objetos identificados por YOLO">
          {summary?.top_classes_24h?.length ? (
            <div style={{ width: "100%", height: 260 }}>
              <ResponsiveContainer>
                <BarChart data={summary.top_classes_24h}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="object_class" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="total" fill="#2E7D32" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="muted">Sin detecciones en el periodo.</p>
          )}
        </Card>

        <Card title="Eventos recientes" subtitle="Últimas detecciones registradas">
          {summary?.recent_events?.length ? (
            <ul className="recent-list">
              {summary.recent_events.map((event) => (
                <li key={event.id}>
                  <span className="event-dot" />
                  <div>
                    <strong>{event.object_class}</strong>
                    <p>{event.zone__name} · {Math.round(event.confidence * 100)}%</p>
                  </div>
                  <small>{new Date(event.detected_at).toLocaleTimeString("es-CO")}</small>
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">Sin eventos recientes.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
