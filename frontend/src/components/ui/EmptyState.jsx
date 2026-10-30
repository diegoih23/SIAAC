export default function EmptyState({ title = "Sin datos", description, action }) {
  return (
    <div className="empty-state">
      <span className="empty-icon">🌱</span>
      <h4>{title}</h4>
      {description && <p>{description}</p>}
      {action}
    </div>
  );
}
