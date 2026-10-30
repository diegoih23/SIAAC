import { useState } from "react";
import { Download, FileText, Plus, RefreshCw } from "lucide-react";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import StatusBadge from "../../../components/ui/StatusBadge";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";
import reportsService from "../services/reportsService";

const today = new Date().toISOString().slice(0, 10);
const EMPTY = {
  title: "",
  report_type: "GENERAL",
  format: "PDF",
  period_start: `${today}T00:00`,
  period_end: `${today}T23:59`,
  zone: "",
};

export default function ReportsPage() {
  const { items, reload, loading } = useApi(endpoints.reports.reports);
  const { items: zones } = useApi(endpoints.crops.zones);
  const [form, setForm] = useState(EMPTY);
  const [showForm, setShowForm] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    await reportsService.create({
      ...form,
      period_start: new Date(form.period_start).toISOString(),
      period_end: new Date(form.period_end).toISOString(),
      zone: form.zone || null,
    });
    setForm(EMPTY);
    setShowForm(false);
    reload();
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Supervisión y reportes</h1>
          <p>Genera reportes PDF o CSV de detecciones, sensores y disuasión.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost" onClick={reload}><RefreshCw size={16} /> Actualizar</button>
          <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}><Plus size={16} /> Nuevo reporte</button>
        </div>
      </header>

      {showForm && (
        <Card title="Generar reporte">
          <form className="form-grid form-inline" onSubmit={submit}>
            <label>Título<input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></label>
            <label>Tipo
              <select value={form.report_type} onChange={(e) => setForm({ ...form, report_type: e.target.value })}>
                <option value="GENERAL">Resumen general</option>
                <option value="DETECTIONS">Detecciones</option>
                <option value="SENSORS">Sensores</option>
                <option value="DISUASION">Disuasión</option>
              </select>
            </label>
            <label>Formato
              <select value={form.format} onChange={(e) => setForm({ ...form, format: e.target.value })}>
                <option value="PDF">PDF</option>
                <option value="CSV">CSV</option>
              </select>
            </label>
            <label>Zona
              <select value={form.zone} onChange={(e) => setForm({ ...form, zone: e.target.value })}>
                <option value="">Todas</option>
                {zones.map((zone) => <option key={zone.id} value={zone.id}>{zone.code} - {zone.name}</option>)}
              </select>
            </label>
            <label>Desde<input type="datetime-local" value={form.period_start} onChange={(e) => setForm({ ...form, period_start: e.target.value })} /></label>
            <label>Hasta<input type="datetime-local" value={form.period_end} onChange={(e) => setForm({ ...form, period_end: e.target.value })} /></label>
            <button className="btn btn-primary">Generar</button>
          </form>
        </Card>
      )}

      <Card title="Historial de reportes" subtitle={loading ? "Cargando…" : `${items.length} reportes`}>
        {items.length === 0 && !loading ? (
          <EmptyState title="Sin reportes generados" description="Crea un reporte para descargar la información del periodo." />
        ) : (
          <table className="data-table">
            <thead><tr><th>Título</th><th>Tipo</th><th>Periodo</th><th>Formato</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              {items.map((report) => (
                <tr key={report.id}>
                  <td><strong>{report.title}</strong><small>{report.zone ? report.zone : "Todas las zonas"}</small></td>
                  <td>{report.report_type_display}</td>
                  <td>{new Date(report.period_start).toLocaleDateString("es-CO")} – {new Date(report.period_end).toLocaleDateString("es-CO")}</td>
                  <td>{report.format}</td>
                  <td><StatusBadge status={report.status} label={report.status_display} /></td>
                  <td>
                    {report.file_url ? (
                      <a className="icon-button" href={report.file_url} target="_blank" rel="noreferrer" title="Descargar"><Download size={18} /></a>
                    ) : (
                      <FileText size={18} className="muted" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
