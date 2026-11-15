import { useEffect, useState } from "react";
import { CheckCircle2, Maximize2, RefreshCw, ShieldAlert, X, XCircle } from "lucide-react";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import StatusBadge from "../../../components/ui/StatusBadge";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";
import detectionService from "../services/detectionService";

export default function DetectionPage() {
  const [filters, setFilters] = useState({ status: "", object_class: "" });
  const [selectedImage, setSelectedImage] = useState(null);
  const { items, reload, loading } = useApi(endpoints.detection.events, { params: filters });

  useEffect(() => {
    const closeWithEscape = (event) => {
      if (event.key === "Escape") setSelectedImage(null);
    };
    window.addEventListener("keydown", closeWithEscape);
    return () => window.removeEventListener("keydown", closeWithEscape);
  }, []);

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
                <div
                  className={`event-thumb ${event.image_url ? "is-clickable" : ""}`}
                  onClick={() => event.image_url && setSelectedImage(event)}
                  role={event.image_url ? "button" : undefined}
                  tabIndex={event.image_url ? 0 : undefined}
                  onKeyDown={(keyboardEvent) => {
                    if (event.image_url && (keyboardEvent.key === "Enter" || keyboardEvent.key === " ")) {
                      setSelectedImage(event);
                    }
                  }}
                >
                  {event.image_url ? <><img src={event.image_url} alt={event.object_class} /><span><Maximize2 size={15} /></span></> : <ShieldAlert size={26} />}
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
      {selectedImage && (
        <div className="image-lightbox" role="dialog" aria-modal="true" aria-label="Imagen ampliada" onClick={() => setSelectedImage(null)}>
          <div className="image-lightbox-content" onClick={(event) => event.stopPropagation()}>
            <button className="image-lightbox-close" type="button" onClick={() => setSelectedImage(null)} aria-label="Cerrar imagen">
              <X size={22} />
            </button>
            <img src={selectedImage.image_url} alt={`Detección de ${selectedImage.object_class}`} />
            <div className="image-lightbox-caption">
              <strong>{selectedImage.object_class} · {Math.round(selectedImage.confidence * 100)}%</strong>
              <span>{selectedImage.zone_name} · {new Date(selectedImage.detected_at).toLocaleString("es-CO")}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
