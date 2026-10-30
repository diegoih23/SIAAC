import { useState } from "react";
import { CheckCircle2, RefreshCw, ShieldAlert, XCircle } from "lucide-react";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import StatusBadge from "../../../components/ui/StatusBadge";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";
import detectionService from "../services/detectionService";

export default function DetectionPage() {
  const [filters, setFilters] = useState({ status: "", object_class: "" });
  const { items, reload, loading } = useApi(endpoints.detection.events, { params: filters });

  const review = async (id, status) => {
    await detectionService.reviewEvent(id, { status });
    reload();
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Detecciones de IA</h1>
          <p>Eventos generados por YOLO en las cámaras de las zonas.</p>
        </div>
        <button className="btn btn-ghost" onClick={reload}><RefreshCw size={16} /> Actualizar</button>
      </header>

      <div className="filters-bar">
        <label>Estado
          <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
            <option value="">Todos</option>
            <option value="NEW">Nuevos</option>
            <option value="VERIFIED">Verificados</option>
            <option value="FALSE_POSITIVE">Falso positivo</option>
            <option value="ATTENDED">Atendidos</option>
          </select>
        </label>
        <label>Clase
          <input placeholder="person, dog…" value={filters.object_class} onChange={(e) => setFilters({ ...filters, object_class: e.target.value })} />
        </label>
      </div>

      <Card title="Eventos" subtitle={loading ? "Cargando…" : `${items.length} eventos`}>
        {items.length === 0 && !loading ? (
          <EmptyState title="Sin detecciones" description="Cuando YOLO detecte un objeto aparecerá aquí." />
        ) : (
          <div className="event-list">
            {items.map((event) => (
              <article className="event-row" key={event.id}>
                <div className="event-thumb">
                  {event.image_url ? <img src={event.image_url} alt={event.object_class} /> : <ShieldAlert size={26} />}
                </div>
                <div className="event-info">
                  <strong>{event.object_class} <span className="confidence">{Math.round(event.confidence * 100)}%</span></strong>
                  <p>{event.zone_name} · {event.device_name || "Dispositivo no asignado"}</p>
                  <small>{new Date(event.detected_at).toLocaleString("es-CO")}</small>
                </div>
                <StatusBadge status={event.status} label={event.status} />
                {event.status === "NEW" && (
                  <div className="event-actions">
                    <button className="icon-button success" title="Verificar" onClick={() => review(event.id, "VERIFIED")}><CheckCircle2 size={18} /></button>
                    <button className="icon-button danger" title="Falso positivo" onClick={() => review(event.id, "FALSE_POSITIVE")}><XCircle size={18} /></button>
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
