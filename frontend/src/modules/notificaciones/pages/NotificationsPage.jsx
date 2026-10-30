import { useCallback } from "react";
import { Bell, CheckCheck, RefreshCw } from "lucide-react";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import StatusBadge from "../../../components/ui/StatusBadge";
import { useApi } from "../../../hooks/useApi";
import { useWebSocket } from "../../../hooks/useWebSocket";
import { endpoints } from "../../../api/endpoints";
import notificationsService from "../services/notificationsService";

export default function NotificationsPage() {
  const { items, reload, loading } = useApi(endpoints.notifications.list);

  const onMessage = useCallback(() => reload(), [reload]);
  useWebSocket("/ws/notifications/", { onMessage });

  const markAll = async () => {
    await notificationsService.markAllRead();
    reload();
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Notificaciones</h1>
          <p>Avisos de detecciones, dispositivos y reportes.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost" onClick={reload}><RefreshCw size={16} /> Actualizar</button>
          <button className="btn btn-primary" onClick={markAll}><CheckCheck size={16} /> Marcar todas como leídas</button>
        </div>
      </header>

      <Card title="Bandeja de entrada" subtitle={loading ? "Cargando…" : `${items.length} notificaciones`}>
        {items.length === 0 && !loading ? (
          <EmptyState title="Todo al día" description="No tienes notificaciones pendientes." />
        ) : (
          <ul className="notification-list">
            {items.map((notification) => (
              <li key={notification.id} className={notification.is_read ? "read" : "unread"}>
                <span className={`notif-icon priority-${notification.priority}`}><Bell size={18} /></span>
                <div className="notif-body">
                  <header>
                    <strong>{notification.title}</strong>
                    <StatusBadge status={notification.priority} label={notification.priority_display} />
                  </header>
                  <p>{notification.message}</p>
                  <small>{new Date(notification.created_at).toLocaleString("es-CO")} · {notification.category_display}</small>
                </div>
                {!notification.is_read && (
                  <button className="btn btn-ghost" onClick={() => notificationsService.markRead(notification.id).then(reload)}>
                    Marcar leída
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
