import { useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import StatusBadge from "../../../components/ui/StatusBadge";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";
import cropsService from "../services/cropsService";

const EMPTY = { name: "", variety: "", scientific_name: "", status: "GROWING" };

export default function CropsPage() {
  const { items, loading, reload } = useApi(endpoints.crops.crops);
  const [form, setForm] = useState(EMPTY);
  const [showForm, setShowForm] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    await cropsService.createCrop(form);
    setForm(EMPTY);
    setShowForm(false);
    reload();
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Cultivos</h1>
          <p>Registro de especies sembradas y su estado fenológico.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost" onClick={reload}><RefreshCw size={16} /> Actualizar</button>
          <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}><Plus size={16} /> Nuevo cultivo</button>
        </div>
      </header>

      {showForm && (
        <Card title="Registrar cultivo">
          <form className="form-grid form-inline" onSubmit={submit}>
            <label>Nombre<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label>Variedad<input value={form.variety} onChange={(e) => setForm({ ...form, variety: e.target.value })} /></label>
            <label>Nombre científico<input value={form.scientific_name} onChange={(e) => setForm({ ...form, scientific_name: e.target.value })} /></label>
            <label>Estado
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                <option value="PLANNED">Planificado</option>
                <option value="GROWING">En crecimiento</option>
                <option value="HARVEST">En cosecha</option>
                <option value="HARVESTED">Cosechado</option>
              </select>
            </label>
            <button className="btn btn-primary">Guardar</button>
          </form>
        </Card>
      )}

      <Card title="Listado de cultivos" subtitle={loading ? "Cargando…" : `${items.length} registros`}>
        {items.length === 0 && !loading ? (
          <EmptyState title="Aún no hay cultivos" description="Crea el primer cultivo para asociar zonas de monitoreo." />
        ) : (
          <table className="data-table">
            <thead><tr><th>Nombre</th><th>Variedad</th><th>Estado</th><th>Zonas</th><th>Creado</th></tr></thead>
            <tbody>
              {items.map((crop) => (
                <tr key={crop.id}>
                  <td><strong>{crop.name}</strong><small>{crop.scientific_name}</small></td>
                  <td>{crop.variety || "—"}</td>
                  <td><StatusBadge status={crop.status} label={crop.status} /></td>
                  <td>{crop.zones_count}</td>
                  <td>{new Date(crop.created_at).toLocaleDateString("es-CO")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
