import { useState } from "react";
import { MapPin, Plus, RefreshCw } from "lucide-react";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import StatusBadge from "../../../components/ui/StatusBadge";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";
import cropsService from "../services/cropsService";

const EMPTY = { name: "", code: "", crop: "", latitude: "", longitude: "", area_m2: "" };

export default function ZonesPage() {
  const { items, reload, loading } = useApi(endpoints.crops.zones);
  const { items: crops } = useApi(endpoints.crops.crops);
  const [form, setForm] = useState(EMPTY);
  const [showForm, setShowForm] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    await cropsService.createZone({
      ...form,
      crop: form.crop || null,
      latitude: form.latitude || null,
      longitude: form.longitude || null,
      area_m2: form.area_m2 || null,
    });
    setForm(EMPTY);
    setShowForm(false);
    reload();
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
          <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}><Plus size={16} /> Nueva zona</button>
        </div>
      </header>

      {showForm && (
        <Card title="Registrar zona">
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
            <button className="btn btn-primary">Guardar</button>
          </form>
        </Card>
      )}

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
          </article>
        ))}
      </div>

      {items.length === 0 && !loading && (
        <EmptyState title="Sin zonas registradas" description="Crea una zona para comenzar a monitorear." />
      )}
    </div>
  );
}
