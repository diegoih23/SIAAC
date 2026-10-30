import { useState } from "react";
import { Navigate } from "react-router-dom";
import { Leaf } from "lucide-react";
import { useAuthStore } from "../../../store/authStore";

export default function LoginPage() {
  const { login, loading, error, isAuthenticated } = useAuthStore();
  const [form, setForm] = useState({ username: "", password: "" });

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  const handleSubmit = async (event) => {
    event.preventDefault();
    await login(form.username, form.password);
  };

  return (
    <div className="auth-screen">
      <section className="auth-brand">
        <span className="auth-logo"><Leaf size={36} /></span>
        <h1>SIAAC</h1>
        <p>Sistema Inteligente de Agricultura Asistida por Computadora</p>
        <ul>
          <li>Monitoreo en tiempo real con ESP32 y Raspberry Pi.</li>
          <li>Detección de intrusiones con visión artificial YOLO.</li>
          <li>Respuesta disuasiva automática y notificaciones.</li>
        </ul>
      </section>

      <section className="auth-panel">
        <div className="auth-card">
          <h2>Iniciar sesión</h2>
          <p className="muted">Accede con las credenciales asignadas por el administrador.</p>

          <form onSubmit={handleSubmit} className="form-grid">
            <label>
              Usuario
              <input
                autoFocus
                required
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                placeholder="usuario.siaac"
              />
            </label>
            <label>
              Contraseña
              <input
                required
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                placeholder="••••••••"
              />
            </label>
            {error && <p className="form-error">{error}</p>}
            <button className="btn btn-primary" disabled={loading}>
              {loading ? "Validando…" : "Entrar"}
            </button>
          </form>

          <p className="auth-foot">¿Olvidaste tu contraseña? Contacta al administrador.</p>
        </div>
      </section>
    </div>
  );
}
