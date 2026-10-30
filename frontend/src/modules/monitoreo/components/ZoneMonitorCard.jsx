import { Activity, Camera, Cpu } from "lucide-react";
import SensorTile from "./SensorTile";

export default function ZoneMonitorCard({ zone, readings = {}, cameras = [] }) {
  return (
    <article className="monitor-card">
      <header>
        <div>
          <span className="zone-code">{zone.code}</span>
          <h3>{zone.name}</h3>
          <p className="muted">{zone.crop_name || "Sin cultivo"}</p>
        </div>
        <span className="live-pill"><i /> EN VIVO</span>
      </header>

      <div className="monitor-preview">
        <Camera size={30} />
        <span>Stream de la cámara</span>
        <small>{cameras.length} cámara(s) configurada(s)</small>
      </div>

      <div className="sensor-row">
        {Object.entries(readings).slice(0, 4).map(([type, reading]) => (
          <SensorTile key={type} type={type} value={reading.value} unit={reading.unit} />
        ))}
        {Object.keys(readings).length === 0 && <p className="muted">Esperando lecturas del ESP32…</p>}
      </div>

      <footer>
        <span><Cpu size={14} /> {zone.devices_count} dispositivos</span>
        <span><Activity size={14} /> {zone.is_active ? "Monitoreando" : "Inactiva"}</span>
      </footer>
    </article>
  );
}
