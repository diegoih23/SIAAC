const LABELS = {
  PIR: { label: "Movimiento", unit: "", icon: "👁️" },
  TEMP: { label: "Temperatura", unit: "°C", icon: "🌡️" },
  HUM: { label: "Humedad", unit: "%", icon: "💧" },
  SOIL: { label: "Suelo", unit: "%", icon: "🌱" },
  LIGHT: { label: "Luz", unit: "lx", icon: "☀️" },
};

export default function SensorTile({ type, value, unit }) {
  const meta = LABELS[type] || { label: type, unit, icon: "📡" };
  return (
    <div className={`sensor-tile ${type === "PIR" && value > 0 ? "sensor-alert" : ""}`}>
      <span className="sensor-icon">{meta.icon}</span>
      <div>
        <small>{meta.label}</small>
        <strong>{value ?? "—"}{meta.unit}</strong>
      </div>
    </div>
  );
}
