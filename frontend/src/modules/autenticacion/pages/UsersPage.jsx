import { useState } from "react";
import { RefreshCw, ShieldCheck, UserCheck, UserX } from "lucide-react";
import Card from "../../../components/ui/Card";
import EmptyState from "../../../components/ui/EmptyState";
import { useApi } from "../../../hooks/useApi";
import { endpoints } from "../../../api/endpoints";
import authService from "../services/authService";

export default function UsersPage() {
  const { items, loading, error, reload } = useApi(endpoints.auth.users);
  const [actionError, setActionError] = useState("");
  const [saving, setSaving] = useState(null);

  const updateRole = async (user, role) => {
    setSaving(user.id);
    setActionError("");
    try {
      await authService.updateUser(user.id, { role });
      reload();
    } catch (requestError) {
      setActionError(requestError.response?.data?.detail || "No se pudo actualizar el rol.");
    } finally {
      setSaving(null);
    }
  };

  const toggleActive = async (user) => {
    setSaving(user.id);
    setActionError("");
    try {
      await authService.toggleUserActive(user.id);
      reload();
    } catch (requestError) {
      setActionError(requestError.response?.data?.detail || "No se pudo actualizar el usuario.");
    } finally {
      setSaving(null);
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Usuarios y roles</h1>
          <p>Administra el acceso de operadores y administradores de SIAAC.</p>
        </div>
        <button className="btn btn-ghost" onClick={reload}><RefreshCw size={16} /> Actualizar</button>
      </header>

      {error && <p className="form-error">{error}</p>}
      {actionError && <p className="form-error">{actionError}</p>}
      <Card title="Usuarios" subtitle={loading ? "Cargando…" : `${items.length} usuarios`}>
        {items.length === 0 && !loading ? (
          <EmptyState title="Sin usuarios" description="No existen usuarios para administrar." />
        ) : (
          <div className="user-management-list">
            {items.map((user) => (
              <article className="user-management-row" key={user.id}>
                <div className="user-management-avatar"><ShieldCheck size={18} /></div>
                <div className="user-management-info">
                  <strong>{user.full_name || user.username}</strong>
                  <span>{user.email} · @{user.username}</span>
                </div>
                <select
                  value={user.role}
                  disabled={saving === user.id}
                  onChange={(event) => updateRole(user, event.target.value)}
                  aria-label={`Rol de ${user.username}`}
                >
                  <option value="ADMIN">Administrador</option>
                  <option value="OPERATOR">Operador</option>
                  <option value="VIEWER">Consulta</option>
                </select>
                <span className={`status-badge tone-${user.is_active ? "success" : "muted"}`}>
                  {user.is_active ? "Activo" : "Inactivo"}
                </span>
                <button
                  className="btn btn-ghost"
                  disabled={saving === user.id}
                  onClick={() => toggleActive(user)}
                  title={user.is_active ? "Desactivar usuario" : "Activar usuario"}
                >
                  {user.is_active ? <UserX size={16} /> : <UserCheck size={16} />}
                </button>
              </article>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
