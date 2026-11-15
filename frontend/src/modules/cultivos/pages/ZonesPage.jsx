import { useState } from "react";
import { Edit2, MapPin, Plus, RefreshCw, Trash2, X } from "lucide-react";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import StatusBadge from "../../../components/ui/StatusBadge";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";
import cropsService from "../services/cropsService";
import { useAuthStore } from "../../../store/authStore";
import LocationPicker from "../components/LocationPicker";

const EMPTY = {
  name: "", code: "", crop: "", description: "",
  latitude: "", longitude: "", area_m2: "", is_active: true,
};

export default function ZonesPage() {
  const user = useAuthStore((state) => state.user);
  const canManage = user?.role === "ADMIN";
  const { items, reload, loading, error } = useApi(endpoints.crops.zones);
  const { items: crops } = useApi(endpoints.crops.crops);
  const [form, setForm] = useState(EMPTY);
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setActionError("");
    const payload = {
      ...form,
      crop: form.crop || null,
      latitude: form.latitude || null,
      longitude: form.longitude || null,
      area_m2: form.area_m2 || null,
    };
    try {
      if (editing) await cropsService.updateZone(editing.id, payload);
      else await cropsService.createZone(payload);
      closeForm();
      reload();
    } catch (requestError) {
      const data = requestError.response?.data;
      setActionError(data?.detail || (data && typeof data === "object"
        ? Object.values(data).flat().join(" ") : "No se pudo guardar la zona."));
    } finally {
      setSaving(false);
    }
  };

  const editZone = (zone) => {
    setEditing(zone);
    setForm({
      name: zone.name || "",
      code: zone.code || "",
      crop: zone.crop || "",
      description: zone.description || "",
      latitude: zone.latitude ?? "",
      longitude: zone.longitude ?? "",
      area_m2: zone.area_m2 ?? "",
      is_active: zone.is_active,
    });
    setActionError("");
    setShowForm(true);
  };

  const deleteZone = async (zone) => {
    if (!window.confirm(`¿Eliminar la zona "${zone.name}"?`)) return;
    setActionError("");
    try {
      await cropsService.deleteZone(zone.id);
      reload();
    } catch (requestError) {
      setActionError(requestError.response?.data?.detail || "No se pudo eliminar la zona.");
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
          <h1>Zonas de cultivo</h1>
          <p>Lotes georreferenciados que agrupan cámaras, sensores y reglas.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost" onClick={reload}><RefreshCw size={16} /> Actualizar</button>
          {canManage && <button className="btn btn-primary" onClick={() => { closeForm(); setShowForm(true); }}><Plus size={16} /> Nueva zona</button>}
        </div>
      </header>

      {showForm && (
        <Card title={editing ? "Editar zona" : "Registrar zona"}>
          <button type="button" className="btn btn-ghost" onClick={closeForm}><X size={16} /> Cancelar</button>
          <form className="form-grid form-inline" onSubmit={submit}>
            <label>Código<input required value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} placeholder="Z-01" /></label>
            <label>Nombre<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label>Cultivo
              <select value={form.crop} onChange={(e) => setForm({ ...form, crop: e.target.value })}>
                <option value="">Sin cultivo</option>
                {crops.map((crop) => <option key={crop.id} value={crop.id}>{crop.name}</option>)}
              </select>
            </label>
            <label>Latitud<input type="number" step="0.000001" value={form.latitude} onChange={(e) => setForm({ ...form, latitude: e.target.value })} /></label>
            <label>Longitud<input type="number" step="0.000001" value={form.longitude} onChange={(e) => setForm({ ...form, longitude: e.target.value })} /></label>
            <label>Área (m²)<input type="number" value={form.area_m2} onChange={(e) => setForm({ ...form, area_m2: e.target.value })} /></label>
            <label>Estado
              <select value={form.is_active ? "true" : "false"} onChange={(e) => setForm({ ...form, is_active: e.target.value === "true" })}>
                <option value="true">Activa</option>
                <option value="false">Inactiva</option>
              </select>
            </label>
            <LocationPicker
              latitude={form.latitude}
              longitude={form.longitude}
              onChange={(latitude, longitude) => setForm({ ...form, latitude, longitude })}
            />
            <label className="form-field-wide">Descripción<textarea rows="3" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
            {actionError && <p className="form-error form-field-wide">{actionError}</p>}
            <button className="btn btn-primary" disabled={saving}>{saving ? "Guardando…" : editing ? "Guardar cambios" : "Guardar"}</button>
          </form>
        </Card>
      )}

      {(error || (actionError && !showForm)) && <p className="form-error">{error || actionError}</p>}
      <div className="zone-grid">
        {items.map((zone) => (
          <article className="zone-card" key={zone.id}>
            <header>
              <span className="zone-code">{zone.code}</span>
              <StatusBadge status={zone.is_active ? "ONLINE" : "OFFLINE"} label={zone.is_active ? "Activa" : "Inactiva"} />
            </header>
            <h3>{zone.name}</h3>
            <p className="muted">{zone.crop_name || "Sin cultivo asignado"}</p>
            <footer>
              <span><MapPin size={14} /> {zone.latitude ?? "—"}, {zone.longitude ?? "—"}</span>
              <span>{zone.devices_count} dispositivos</span>
            </footer>
            {canManage && <div className="table-actions">
              <button className="btn btn-ghost" title="Editar zona" onClick={() => editZone(zone)}><Edit2 size={15} /></button>
              <button className="btn btn-ghost" title="Eliminar zona" onClick={() => deleteZone(zone)}><Trash2 size={15} /></button>
            </div>}
          </article>
        ))}
      </div>

      {items.length === 0 && !loading && (
        <EmptyState title="Sin zonas registradas" description="Crea una zona para comenzar a monitorear." />
      )}
    </div>
  );
}
