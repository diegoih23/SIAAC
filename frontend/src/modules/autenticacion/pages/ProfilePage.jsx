import { useState } from "react";
import Card from "../../../components/ui/Card";
import { useAuthStore } from "../../../store/authStore";
import authService from "../services/authService";

export default function ProfilePage() {
  const { user, fetchMe } = useAuthStore();
  const [form, setForm] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    email: user?.email || "",
    phone: user?.phone || "",
  });
  const [passwords, setPasswords] = useState({ current_password: "", new_password: "" });
  const [message, setMessage] = useState("");
  const [twoFactor, setTwoFactor] = useState(Boolean(user?.two_factor_enabled));

  const saveProfile = async (event) => {
    event.preventDefault();
    await authService.updateProfile(form);
    await fetchMe();
    setMessage("Perfil actualizado.");
  };

  const changePassword = async (event) => {
    event.preventDefault();
    try {
      await authService.changePassword(passwords);
      setMessage("Contraseña actualizada. Vuelve a iniciar sesión.");
      setPasswords({ current_password: "", new_password: "" });
    } catch (error) {
      setMessage(JSON.stringify(error.response?.data || "Error al actualizar."));
    }
  };

  const toggleTwoFactor = async () => {
    try {
      const { data } = await authService.toggleTwoFactor(!twoFactor);
      setTwoFactor(data.two_factor_enabled);
      setMessage(data.two_factor_enabled ? "Autenticación de dos factores activada." : "Autenticación de dos factores desactivada.");
    } catch (error) {
      setMessage(error.response?.data?.detail || "No se pudo actualizar la seguridad.");
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Mi perfil</h1>
          <p>Datos de la cuenta y seguridad de la sesión.</p>
        </div>
      </header>

      {message && <div className="alert alert-info">{message}</div>}

      <div className="grid-2">
        <Card title="Datos personales" subtitle={`Rol: ${user?.role || "—"}`}>
          <form className="form-grid" onSubmit={saveProfile}>
            <label>Nombre<input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /></label>
            <label>Apellido<input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></label>
            <label>Correo<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
            <label>Teléfono<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
            <button className="btn btn-primary">Guardar cambios</button>
          </form>
        </Card>

        <Card title="Cambiar contraseña" subtitle="Se cerrarán las sesiones activas.">
          <form className="form-grid" onSubmit={changePassword}>
            <label>Contraseña actual<input type="password" required value={passwords.current_password} onChange={(e) => setPasswords({ ...passwords, current_password: e.target.value })} /></label>
            <label>Nueva contraseña<input type="password" required value={passwords.new_password} onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })} /></label>
            <button className="btn btn-secondary">Actualizar contraseña</button>
          </form>
        </Card>

        <Card title="Seguridad de acceso" subtitle="Protege la cuenta con un código adicional por correo.">
          <div className="security-toggle-row">
            <div>
              <strong>Autenticación de dos factores</strong>
              <p className="muted">Solicitar un código al iniciar sesión.</p>
            </div>
            <button type="button" className={`toggle-switch ${twoFactor ? "on" : ""}`} onClick={toggleTwoFactor} aria-pressed={twoFactor}>
              <span />
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
}
