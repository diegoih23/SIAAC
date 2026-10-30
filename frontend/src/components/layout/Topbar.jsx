import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bell, LogOut, UserCircle } from "lucide-react";
import api from "../../api/client";
import { endpoints } from "../../api/endpoints";
import { useAuthStore } from "../../store/authStore";

export default function Topbar() {
  const { user, logout } = useAuthStore();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    api
      .get(endpoints.notifications.unreadCount)
      .then(({ data }) => setUnread(data.unread))
      .catch(() => setUnread(0));
  }, []);

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
        <Link to="/notifications" className="icon-button" aria-label="Notificaciones">
          <Bell size={20} />
          {unread > 0 && <span className="badge">{unread}</span>}
        </Link>
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
