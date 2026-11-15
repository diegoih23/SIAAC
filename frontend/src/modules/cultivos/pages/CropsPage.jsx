import { useState } from "react";
import { Edit2, Plus, RefreshCw, Trash2, X } from "lucide-react";
import { useAuthStore } from "../../../store/authStore";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import StatusBadge from "../../../components/ui/StatusBadge";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";
import cropsService from "../services/cropsService";

const EMPTY = {
  name: "", variety: "", scientific_name: "", description: "",
  planting_date: "", harvest_date: "", status: "GROWING", assigned_users: [],
};

export default function CropsPage() {
  const user = useAuthStore((state) => state.user);
  const canManage = user?.role === "ADMIN";
  const { items, loading, error, reload } = useApi(endpoints.crops.crops);
  const { items: users } = useApi(endpoints.auth.users, { enabled: canManage });
  const [form, setForm] = useState(EMPTY);
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setActionError("");
    try {
      if (editing) await cropsService.updateCrop(editing.id, form);
      else await cropsService.createCrop(form);
      setForm(EMPTY);
      setEditing(null);
      setShowForm(false);
      reload();
    } catch (requestError) {
      const data = requestError.response?.data;
      setActionError(data?.detail || (data && typeof data === "object"
        ? Object.values(data).flat().join(" ") : "No se pudo guardar el cultivo."));
    } finally {
      setSaving(false);
    }
  };

  const editCrop = (crop) => {
    setEditing(crop);
    setForm({
      name: crop.name || "",
      variety: crop.variety || "",
      scientific_name: crop.scientific_name || "",
      description: crop.description || "",
      planting_date: crop.planting_date || "",
      harvest_date: crop.harvest_date || "",
      status: crop.status || "GROWING",
      assigned_users: crop.assigned_users || [],
    });
    setActionError("");
    setShowForm(true);
  };

  const deleteCrop = async (crop) => {
    const warning = crop.zones_count
      ? `Este cultivo tiene ${crop.zones_count} zona(s) asociada(s). Al eliminarlo también se desvincularán. ¿Continuar?`
      : `¿Eliminar el cultivo "${crop.name}"?`;
    if (!window.confirm(warning)) return;
    setActionError("");
    try {
      await cropsService.deleteCrop(crop.id);
      reload();
    } catch (requestError) {
      setActionError(requestError.response?.data?.detail || "No se pudo eliminar el cultivo.");
    }
  };

  const closeForm = () => {
    setForm(EMPTY);
    setEditing(null);
    setActionError("");
    setShowForm(false);
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
          {canManage && <button className="btn btn-primary" onClick={() => { closeForm(); setShowForm(true); }}><Plus size={16} /> Nuevo cultivo</button>}
        </div>
      </header>

      {showForm && (
        <Card title={editing ? "Editar cultivo" : "Registrar cultivo"}>
          <button type="button" className="btn btn-ghost" onClick={closeForm}><X size={16} /> Cancelar</button>
          <form className="form-grid form-inline" onSubmit={submit}>
            <label>Nombre<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label>Variedad<input value={form.variety} onChange={(e) => setForm({ ...form, variety: e.target.value })} /></label>
            <label>Nombre científico<input value={form.scientific_name} onChange={(e) => setForm({ ...form, scientific_name: e.target.value })} /></label>
            <label>Fecha de siembra<input type="date" value={form.planting_date} onChange={(e) => setForm({ ...form, planting_date: e.target.value })} /></label>
            <label>Fecha de cosecha<input type="date" value={form.harvest_date} onChange={(e) => setForm({ ...form, harvest_date: e.target.value })} /></label>
            <label>Estado
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                <option value="PLANNED">Planificado</option>
                <option value="GROWING">En crecimiento</option>
                <option value="HARVEST">En cosecha</option>
                <option value="HARVESTED">Cosechado</option>
              </select>
            </label>
            {canManage && <label>Usuarios asignados
              <select
                multiple
                value={form.assigned_users.map(String)}
                onChange={(event) => setForm({
                  ...form,
                  assigned_users: Array.from(event.target.selectedOptions, (option) => option.value),
                })}
              >
                {users.map((assignedUser) => (
                  <option key={assignedUser.id} value={assignedUser.id}>
                    {assignedUser.full_name || assignedUser.username}
                  </option>
                ))}
              </select>
              <small className="muted">Mantén Ctrl/Cmd para seleccionar varios usuarios.</small>
            </label>}
            <label className="form-field-wide">Descripción<textarea rows="3" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
            {actionError && <p className="form-error form-field-wide">{actionError}</p>}
            <button className="btn btn-primary" disabled={saving}>{saving ? "Guardando…" : editing ? "Guardar cambios" : "Guardar"}</button>
          </form>
        </Card>
      )}

      <Card title="Listado de cultivos" subtitle={loading ? "Cargando…" : `${items.length} registros`}>
        {(error || (actionError && !showForm)) && <p className="form-error">{error || actionError}</p>}
        {items.length === 0 && !loading ? (
          <EmptyState title="Aún no hay cultivos" description="Crea el primer cultivo para asociar zonas de monitoreo." />
        ) : (
          <table className="data-table">
            <thead><tr><th>Nombre</th><th>Variedad</th><th>Estado</th><th>Zonas</th><th>Creado</th>{canManage && <th>Acciones</th>}</tr></thead>
            <tbody>
              {items.map((crop) => (
                <tr key={crop.id}>
                  <td><strong>{crop.name}</strong><small>{crop.scientific_name}</small></td>
                  <td>{crop.variety || "—"}</td>
                  <td><StatusBadge status={crop.status} label={crop.status} /></td>
                  <td>{crop.zones_count}</td>
                  <td>{new Date(crop.created_at).toLocaleDateString("es-CO")}</td>
                  {canManage && <td className="table-actions">
                    <button className="btn btn-ghost" title="Editar cultivo" onClick={() => editCrop(crop)}><Edit2 size={15} /></button>
                    <button className="btn btn-ghost" title="Eliminar cultivo" onClick={() => deleteCrop(crop)}><Trash2 size={15} /></button>
                  </td>}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
