import { useState } from "react";
import { Play, Plus, RefreshCw, Siren, Volume2 } from "lucide-react";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import StatusBadge from "../../../components/ui/StatusBadge";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";
import disuasionService from "../services/disuasionService";

const EMPTY = { name: "", zone: "", trigger_classes: "person", min_confidence: 0.6, action: "BOTH", duration_seconds: 15 };

export default function DisuasionPage() {
  const { items: rules, reload, loading } = useApi(endpoints.disuasion.rules);
  const { items: activations, reload: reloadActivations } = useApi(endpoints.disuasion.activations);
  const { items: zones } = useApi(endpoints.crops.zones);
  const [form, setForm] = useState(EMPTY);
  const [showForm, setShowForm] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    await disuasionService.createRule({
      ...form,
      trigger_classes: form.trigger_classes.split(",").map((item) => item.trim()).filter(Boolean),
      zone: form.zone || null,
    });
    setForm(EMPTY);
    setShowForm(false);
    reload();
  };

  const activate = async (id) => {
    await disuasionService.activate(id);
    reloadActivations();
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Respuesta disuasiva</h1>
          <p>Reglas que activan la bocina y las luces del prototipo ante detecciones.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost" onClick={reload}><RefreshCw size={16} /> Actualizar</button>
          <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}><Plus size={16} /> Nueva regla</button>
        </div>
      </header>

      {showForm && (
        <Card title="Configurar regla">
          <form className="form-grid form-inline" onSubmit={submit}>
            <label>Nombre<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label>Zona
              <select required value={form.zone} onChange={(e) => setForm({ ...form, zone: e.target.value })}>
                <option value="">Selecciona…</option>
                {zones.map((zone) => <option key={zone.id} value={zone.id}>{zone.code} - {zone.name}</option>)}
              </select>
            </label>
            <label>Clases (coma)<input value={form.trigger_classes} onChange={(e) => setForm({ ...form, trigger_classes: e.target.value })} /></label>
            <label>Confianza mínima<input type="number" step="0.05" min="0" max="1" value={form.min_confidence} onChange={(e) => setForm({ ...form, min_confidence: e.target.value })} /></label>
            <label>Acción
              <select value={form.action} onChange={(e) => setForm({ ...form, action: e.target.value })}>
                <option value="BOTH">Sirena + luces</option>
                <option value="SIREN">Solo sirena</option>
                <option value="LIGHT">Solo luces</option>
              </select>
            </label>
            <label>Duración (s)<input type="number" value={form.duration_seconds} onChange={(e) => setForm({ ...form, duration_seconds: e.target.value })} /></label>
            <button className="btn btn-primary">Guardar</button>
          </form>
        </Card>
      )}

      <div className="rule-grid">
        {rules.map((rule) => (
          <article className="rule-card" key={rule.id}>
            <header>
              <span className="rule-icon"><Siren size={20} /></span>
              <StatusBadge status={rule.is_active ? "ONLINE" : "OFFLINE"} label={rule.is_active ? "Activa" : "Inactiva"} />
            </header>
            <h3>{rule.name}</h3>
            <p className="muted">{rule.zone_name}</p>
            <ul>
              <li>Clases: {rule.trigger_classes?.join(", ") || "—"}</li>
              <li>Confianza ≥ {Math.round(rule.min_confidence * 100)}%</li>
              <li>Acción: {rule.action_display} · {rule.duration_seconds}s</li>
            </ul>
            <button className="btn btn-danger" onClick={() => activate(rule.id)}><Play size={14} /> Activar prueba</button>
          </article>
        ))}
      </div>

      {rules.length === 0 && !loading && <EmptyState title="Sin reglas configuradas" description="Crea una regla para responder automáticamente a las detecciones." />}

      <Card title="Historial de activaciones" subtitle="Comandos enviados a la bocina y luces">
        <table className="data-table">
          <thead><tr><th>Regla</th><th>Evento</th><th>Estado</th><th>Inicio</th></tr></thead>
          <tbody>
            {activations.map((activation) => (
              <tr key={activation.id}>
                <td>{activation.rule_name || "—"}</td>
                <td>{activation.event || "Manual"}</td>
                <td><StatusBadge status={activation.status} label={activation.status_display} /></td>
                <td>{new Date(activation.started_at).toLocaleString("es-CO")}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {activations.length === 0 && <p className="muted"><Volume2 size={14} /> Sin activaciones registradas.</p>}
      </Card>
    </div>
  );
}
