import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Bell, LogOut, UserCircle } from "lucide-react";
import api from "../../api/client";
import { endpoints } from "../../api/endpoints";
import { useAuthStore } from "../../store/authStore";
import notificationsService from "../../modules/notificaciones/services/notificationsService";

export default function Topbar() {
  const { user, logout } = useAuthStore();
  const [unread, setUnread] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  const loadNotifications = () => {
    api
      .get(endpoints.notifications.list, { params: { page_size: 5 } })
      .then(({ data }) => {
        const items = Array.isArray(data) ? data : data.results || [];
        setNotifications(items.slice(0, 5));
        setUnread(items.filter((item) => !item.is_read).length);
      })
      .catch(() => setUnread(0));
  };

  useEffect(() => {
    loadNotifications();
    const close = (event) => {
      if (!dropdownRef.current?.contains(event.target)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  const markRead = async (notification) => {
    if (!notification.is_read) {
      await notificationsService.markRead(notification.id);
      loadNotifications();
    }
  };

  return (
    <header className="topbar">
      <div>
        <h2 className="topbar-title">Panel de control</h2>
        <p className="topbar-subtitle">
          {new Date().toLocaleDateString("es-CO", {
            weekday: "long", day: "numeric", month: "long", year: "numeric",
          })}
        </p>
      </div>

      <div className="topbar-actions">
        <div className="notification-dropdown" ref={dropdownRef}>
          <button type="button" className="icon-button" aria-label="Notificaciones" aria-expanded={open} onClick={() => { setOpen((value) => !value); if (!open) loadNotifications(); }}>
            <Bell size={20} />
            {unread > 0 && <span className="badge">{unread}</span>}
          </button>
          {open && (
            <div className="notification-menu">
              <header>
                <strong>Notificaciones</strong>
                {unread > 0 && <span>{unread} sin leer</span>}
              </header>
              {notifications.length === 0 ? (
                <p className="notification-menu-empty">No tienes notificaciones nuevas.</p>
              ) : notifications.map((notification) => (
                <button
                  type="button"
                  className={`notification-menu-item ${notification.is_read ? "read" : "unread"}`}
                  key={notification.id}
                  onClick={() => markRead(notification)}
                >
                  <span className="notification-menu-dot" />
                  <span>
                    <strong>{notification.title}</strong>
                    <small>{notification.message}</small>
                    <em>{new Date(notification.created_at).toLocaleString("es-CO")}</em>
                  </span>
                </button>
              ))}
              <Link to="/notifications" className="notification-menu-footer" onClick={() => setOpen(false)}>
                Ver todas las notificaciones
              </Link>
            </div>
          )}
        </div>
        <Link to="/profile" className="user-chip">
          <UserCircle size={22} />
          <span>
            <strong>{user?.full_name || user?.username || "Usuario"}</strong>
            <small>{user?.role || "VIEWER"}</small>
          </span>
        </Link>
        <button className="icon-button" onClick={logout} aria-label="Cerrar sesión">
          <LogOut size={20} />
        </button>
      </div>
    </header>
  );
}
