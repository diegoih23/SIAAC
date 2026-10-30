import { useState } from "react";
import { Cpu, Plus, RefreshCw, Wifi } from "lucide-react";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import StatusBadge from "../../../components/ui/StatusBadge";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";
import detectionService from "../services/detectionService";

const EMPTY = { name: "", device_type: "ESP32", serial_number: "", zone: "" };

export default function DevicesPage() {
  const { items, reload, loading } = useApi(endpoints.detection.devices);
  const { items: zones } = useApi(endpoints.crops.zones);
  const [form, setForm] = useState(EMPTY);
  const [showForm, setShowForm] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    await detectionService.createDevice({ ...form, zone: form.zone || null });
    setForm(EMPTY);
    setShowForm(false);
    reload();
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Dispositivos</h1>
          <p>ESP32, Raspberry Pi y cámaras registradas en el prototipo.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost" onClick={reload}><RefreshCw size={16} /> Actualizar</button>
          <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}><Plus size={16} /> Registrar</button>
        </div>
      </header>

      {showForm && (
        <Card title="Nuevo dispositivo" subtitle="La API key se genera automáticamente al guardar.">
          <form className="form-grid form-inline" onSubmit={submit}>
            <label>Nombre<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label>Tipo
              <select value={form.device_type} onChange={(e) => setForm({ ...form, device_type: e.target.value })}>
                <option value="ESP32">ESP32</option>
                <option value="RPI">Raspberry Pi</option>
                <option value="CAMERA">Cámara IP</option>
              </select>
            </label>
            <label>Serie<input required value={form.serial_number} onChange={(e) => setForm({ ...form, serial_number: e.target.value })} /></label>
            <label>Zona
              <select value={form.zone} onChange={(e) => setForm({ ...form, zone: e.target.value })}>
                <option value="">Sin zona</option>
                {zones.map((zone) => <option key={zone.id} value={zone.id}>{zone.code} - {zone.name}</option>)}
              </select>
            </label>
            <button className="btn btn-primary">Guardar</button>
          </form>
        </Card>
      )}

      <div className="device-grid">
        {items.map((device) => (
          <article className="device-card" key={device.id}>
            <header>
              <span className="device-icon"><Cpu size={22} /></span>
              <StatusBadge status={device.status} label={device.status} />
            </header>
            <h3>{device.name}</h3>
            <p className="muted">{device.device_type_display} · {device.serial_number}</p>
            <dl>
              <div><dt>Zona</dt><dd>{device.zone_name || "—"}</dd></div>
              <div><dt>IP</dt><dd>{device.ip_address || "—"}</dd></div>
              <div><dt>Última señal</dt><dd>{device.last_seen ? new Date(device.last_seen).toLocaleString("es-CO") : "—"}</dd></div>
            </dl>
            <footer>
              <button className="btn btn-ghost" onClick={() => detectionService.heartbeat(device.id, {}).then(reload)}>
                <Wifi size={14} /> Probar conexión
              </button>
            </footer>
          </article>
        ))}
      </div>

      {items.length === 0 && !loading && <EmptyState title="Sin dispositivos" description="Registra el ESP32 o la Raspberry Pi del prototipo." />}
    </div>
  );
}
