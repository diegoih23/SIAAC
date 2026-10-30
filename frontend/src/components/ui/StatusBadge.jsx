const COLORS = {
  ONLINE: "success",
  READY: "success",
  VERIFIED: "success",
  EXECUTED: "success",
  NEW: "info",
  PENDING: "warning",
  SENT: "info",
  OFFLINE: "muted",
  FAILED: "danger",
  FALSE_POSITIVE: "danger",
  CRITICAL: "danger",
  HIGH: "warning",
  NORMAL: "info",
  LOW: "muted",
};

export default function StatusBadge({ status, label }) {
  const tone = COLORS[status] || "muted";
  return <span className={`status-badge tone-${tone}`}>{label || status}</span>;
}
