export default function StatCard({ label, value, hint, accent = "green", icon: Icon }) {
  return (
    <article className={`stat-card accent-${accent}`}>
      <div>
        <p className="stat-label">{label}</p>
        <strong className="stat-value">{value ?? "—"}</strong>
        {hint && <p className="stat-hint">{hint}</p>}
      </div>
      {Icon && <span className="stat-icon"><Icon size={24} /></span>}
    </article>
  );
}
