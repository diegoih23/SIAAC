import { useEffect, useRef, useState } from "react";
import { Navigate } from "react-router-dom";
import { Eye, EyeOff, LockKeyhole, Moon, Radio, ShieldCheck, Sprout, Sun } from "lucide-react";
import { useAuthStore } from "../../../store/authStore";
import authService from "../services/authService";

function LogoSiaac() {
  return (
    <div className="siaac-logo" aria-label="Logo SIAAC">
      <svg viewBox="0 0 64 64" role="img">
        <defs>
          <linearGradient id="logoLeaf" x1="0" x2="1" y1="1" y2="0">
            <stop offset="0" stopColor="#62d795" />
            <stop offset="1" stopColor="#c2ed93" />
          </linearGradient>
        </defs>
        <path d="M31 52V29" fill="none" stroke="#e6f8d2" strokeLinecap="round" strokeWidth="3.5" />
        <path d="M31 37C18 37 12 29 13 18c11 0 18 7 18 19Z" fill="url(#logoLeaf)" />
        <path d="M31 29C31 17 40 10 53 11c0 11-8 18-22 18Z" fill="#8ae2a8" />
        <path d="M19 50c8 4 19 4 27 0" fill="none" opacity=".6" stroke="#b8e8b4" strokeLinecap="round" strokeWidth="2" />
        <circle cx="31" cy="53" r="3" fill="#f0c873" />
      </svg>
    </div>
  );
}

function BuhoVigilante({ passwordFocused, usernameFocused }) {
  return (
    <div className={`mascot ${passwordFocused ? "mascot-password" : ""} ${usernameFocused ? "mascot-username" : ""}`} aria-hidden="true">
      <div className="mascot-signal signal-one" />
      <div className="mascot-signal signal-two" />
      <svg viewBox="0 0 220 190" role="presentation">
        <defs>
          <linearGradient id="owlBody" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0" stopColor="#536b80" />
            <stop offset="1" stopColor="#1d2d42" />
          </linearGradient>
          <linearGradient id="owlChest" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stopColor="#f5e9d4" />
            <stop offset="1" stopColor="#cdb99c" />
          </linearGradient>
        </defs>
        <ellipse cx="110" cy="166" rx="64" ry="11" fill="#0a1727" opacity=".5" />
        <path d="M56 148c-9-29-6-74 18-101C87 27 101 22 110 22s23 5 36 25c24 27 27 72 18 101-13 21-95 21-108 0Z" fill="url(#owlBody)" />
        <path d="M75 55 59 21l34 22M145 55l16-34-34 22" fill="#324960" />
        <path d="M68 55c-11 5-18 19-14 33 10 32 45 38 56 9 11 29 46 23 56-9 4-14-3-28-14-33-12-5-30 1-42 14-12-13-30-19-42-14Z" fill="#d6c5a9" />
        <circle cx="84" cy="79" r="20" fill="#f6f0e5" />
        <circle cx="136" cy="79" r="20" fill="#f6f0e5" />
        <circle cx="85" cy="80" r="9" fill="#112236" className="mascot-eye" />
        <circle cx="135" cy="80" r="9" fill="#112236" className="mascot-eye" />
        <circle cx="88" cy="76" r="3" fill="#fff" />
        <circle cx="138" cy="76" r="3" fill="#fff" />
        <path d="m101 91 9-9 9 9-9 13Z" fill="#e2a44e" />
        <path d="M78 121c18-16 46-16 64 0v31H78Z" fill="url(#owlChest)" />
        <path d="M89 122c7 9 14 13 21 15 7-2 14-6 21-15" fill="none" stroke="#b39a7b" strokeWidth="4" strokeLinecap="round" />
        <path d="M66 137 45 153l30-5M154 137l21 16-30-5" fill="#465e73" />
        <circle cx="179" cy="43" r="5" fill="#8de3b0" className="mascot-status-light" />
      </svg>
      <span className="mascot-label"><Radio size={12} /> vigilancia activa</span>
    </div>
  );
}

function SegundoFactor({ challenge, onBack }) {
  const { completeTwoFactor, loading, error } = useAuthStore();
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [verificationSeconds, setVerificationSeconds] = useState(challenge.expiresIn || 600);
  const refs = useRef([]);

  useEffect(() => {
    if (verificationSeconds <= 0) return undefined;
    const timer = window.setInterval(() => setVerificationSeconds((value) => value - 1), 1000);
    return () => window.clearInterval(timer);
  }, [verificationSeconds]);

  const updateDigit = (index, value) => {
    const next = [...code];
    next[index] = value.replace(/\D/g, "").slice(-1);
    setCode(next);
    if (next[index] && index < 5) refs.current[index + 1]?.focus();
  };

  const submit = async (event) => {
    event.preventDefault();
    await completeTwoFactor(challenge.challengeId, code.join(""));
  };

  return (
    <div className="recovery-content two-factor-content">
      <button type="button" className="recovery-back" onClick={onBack}>← Usar otra cuenta</button>
      <span className="recovery-icon"><ShieldCheck size={21} /></span>
      <span className="auth-card-kicker">Segundo factor activo</span>
      <h2>Confirma tu identidad</h2>
      <p className="muted">Enviamos un código de 6 dígitos al correo asociado a tu cuenta.</p>
      <div className="recovery-progress"><i className="active" /><i className="active" /><i /></div>
      <form className="form-grid recovery-form" onSubmit={submit}>
        <p className="verification-countdown" role="timer">
          {verificationSeconds > 0
            ? `El código vence en ${Math.floor(verificationSeconds / 60)}:${String(verificationSeconds % 60).padStart(2, "0")}`
            : "El código expiró. Solicita un nuevo acceso."}
        </p>
        <div className="otp-inputs" aria-label="Código de doble factor">
          {code.map((digit, index) => <input key={index} ref={(element) => { refs.current[index] = element; }} autoFocus={index === 0} inputMode="numeric" maxLength={1} value={digit} onChange={(event) => updateDigit(index, event.target.value)} aria-label={`Dígito ${index + 1}`} />)}
        </div>
        {error && <p className="form-error"><LockKeyhole size={14} /> {error}</p>}
        <button className="btn btn-primary auth-submit" disabled={loading || verificationSeconds <= 0 || code.join("").length !== 6}>{loading ? "Verificando…" : "Confirmar acceso"}<span>→</span></button>
      </form>
      <p className="auth-foot">El código tiene una vigencia de 10 minutos.</p>
    </div>
  );
}

function RegistroUsuario({ onBack, onRegistered }) {
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", phone: "", username: "", password: "", password_confirm: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));
  const submit = async (event) => {
    event.preventDefault();
    setLoading(true); setError("");
    try {
      const { data } = await authService.register(form);
      onRegistered(data.username, form.email);
    } catch (requestError) {
      const data = requestError.response?.data;
      setError(data?.detail || (data && typeof data === "object" ? Object.values(data).flat().join(" ") : "No se pudo crear la cuenta."));
    } finally { setLoading(false); }
  };

  return (
    <div className="recovery-content registration-content">
      <button type="button" className="recovery-back" onClick={onBack}>← Volver al inicio de sesión</button>
      <span className="recovery-icon"><Sprout size={21} /></span>
      <span className="auth-card-kicker">Nueva cuenta</span>
      <h2>Únete a SIAAC</h2>
      <p className="muted">Registra tus datos para acceder al monitoreo de cultivos.</p>
      <form className="form-grid recovery-form registration-form" onSubmit={submit}>
        <div className="registration-fields">
          <label className="auth-field"><span>Nombre</span><input required maxLength={60} value={form.first_name} onChange={(event) => update("first_name", event.target.value)} placeholder="Tu nombre" /></label>
          <label className="auth-field"><span>Apellido</span><input required maxLength={80} value={form.last_name} onChange={(event) => update("last_name", event.target.value)} placeholder="Tu apellido" /></label>
        </div>
        <label className="auth-field"><span>Correo electrónico</span><input required type="email" maxLength={254} value={form.email} onChange={(event) => update("email", event.target.value)} placeholder="tu.correo@ejemplo.com" /></label>
        <div className="registration-fields">
          <label className="auth-field"><span>Celular <small>(opcional)</small></span><input type="tel" maxLength={20} value={form.phone} onChange={(event) => update("phone", event.target.value)} placeholder="+57 300 000 0000" /></label>
          <label className="auth-field"><span>Usuario <small>(opcional)</small></span><input maxLength={30} pattern="[A-Za-z0-9._-]{3,30}" value={form.username} onChange={(event) => update("username", event.target.value)} placeholder="Se genera automáticamente" /></label>
        </div>
        <p className="muted">Si no indicas un usuario, generaremos uno y te lo enviaremos al correo.</p>
        <div className="registration-fields">
          <label className="auth-field"><span>Contraseña</span><input required type="password" minLength={8} maxLength={128} value={form.password} onChange={(event) => update("password", event.target.value)} placeholder="Mínimo 8 caracteres" /></label>
          <label className="auth-field"><span>Confirmar contraseña</span><input required type="password" minLength={8} maxLength={128} value={form.password_confirm} onChange={(event) => update("password_confirm", event.target.value)} placeholder="Repite la contraseña" /></label>
        </div>
        {error && <p className="form-error"><LockKeyhole size={14} /> {error}</p>}
        <button className="btn btn-primary auth-submit" disabled={loading}>{loading ? "Creando cuenta…" : "Crear cuenta"}<span>→</span></button>
      </form>
      <p className="auth-foot">Tus datos se usarán exclusivamente para gestionar el acceso.</p>
    </div>
  );
}

function VerificacionCorreo({ email, username, onBack, onVerified }) {
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("Revisa tu bandeja de entrada para encontrar el código.");
  const [resendSeconds, setResendSeconds] = useState(0);
  const [verificationSeconds, setVerificationSeconds] = useState(120);
  const refs = useRef([]);

  useEffect(() => {
    if (resendSeconds <= 0) return undefined;
    const timer = window.setInterval(() => setResendSeconds((value) => value - 1), 1000);
    return () => window.clearInterval(timer);
  }, [resendSeconds]);

  useEffect(() => {
    if (verificationSeconds <= 0) return undefined;
    const timer = window.setInterval(() => setVerificationSeconds((value) => value - 1), 1000);
    return () => window.clearInterval(timer);
  }, [verificationSeconds]);

  const updateDigit = (index, value) => {
    const next = [...code];
    next[index] = value.replace(/\D/g, "").slice(-1);
    setCode(next); setError("");
    if (next[index] && index < 5) refs.current[index + 1]?.focus();
  };
  const submit = async (event) => {
    event.preventDefault(); setLoading(true); setError("");
    try { await authService.verifyEmail({ email, code: code.join("") }); onVerified(username); }
    catch (requestError) { const data = requestError.response?.data; setError(data?.detail || (data && typeof data === "object" ? Object.values(data).flat().join(" ") : "Código no válido.")); }
    finally { setLoading(false); }
  };
  const resend = async () => {
    if (resendSeconds > 0) return;
    setLoading(true); setError("");
    try {
      const { data } = await authService.resendEmailVerification(email);
      setMessage(data.detail);
      setResendSeconds(60);
      setVerificationSeconds(120);
      setCode(["", "", "", "", "", ""]);
      refs.current[0]?.focus();
    } catch (requestError) {
      const data = requestError.response?.data;
      setError(data?.detail || "No se pudo reenviar el código.");
      if (data?.retry_after) setResendSeconds(data.retry_after);
    }
    finally { setLoading(false); }
  };
  return (
    <div className="recovery-content email-verification-content">
      <button type="button" className="recovery-back" onClick={onBack}>← Volver al registro</button>
      <span className="recovery-icon"><ShieldCheck size={21} /></span>
      <span className="auth-card-kicker">Verificación requerida</span>
      <h2>Confirma tu correo</h2>
      <p className="muted">Enviamos un código de 6 dígitos a <strong>{email}</strong>.</p>
      <div className="recovery-progress"><i className="active" /><i className="active" /><i /></div>
      <form className="form-grid recovery-form" onSubmit={submit}>
        <p className="verification-countdown" role="timer">
          {verificationSeconds > 0
            ? `El código vence en ${Math.floor(verificationSeconds / 60)}:${String(verificationSeconds % 60).padStart(2, "0")}`
            : "El código expiró. Solicita uno nuevo."}
        </p>
        <div className="otp-inputs" aria-label="Código de verificación de correo">
          {code.map((digit, index) => <input key={index} ref={(element) => { refs.current[index] = element; }} autoFocus={index === 0} inputMode="numeric" maxLength={1} value={digit} onChange={(event) => updateDigit(index, event.target.value)} aria-label={`Dígito ${index + 1}`} />)}
        </div>
        {message && <p className="recovery-message"><ShieldCheck size={14} /> {message}</p>}
        {error && <p className="form-error"><LockKeyhole size={14} /> {error}</p>}
        <button className="btn btn-primary auth-submit" disabled={loading || verificationSeconds <= 0 || code.join("").length !== 6}>{loading ? "Verificando…" : "Verificar correo"}<span>→</span></button>
        <p className="resend-code">¿No recibiste el código? <button type="button" onClick={resend} disabled={loading || resendSeconds > 0}>{resendSeconds > 0 ? `Reenviar en ${resendSeconds}s` : "Reenviar código"}</button></p>
      </form>
      <p className="auth-foot">El código tiene una vigencia de 2 minutos.</p>
    </div>
  );
}

function RecuperacionPassword({ onBack }) {
  const [step, setStep] = useState("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [seconds, setSeconds] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const codeRefs = useRef([]);

  useEffect(() => {
    if (seconds <= 0) return undefined;
    const timer = window.setInterval(() => setSeconds((value) => value - 1), 1000);
    return () => window.clearInterval(timer);
  }, [seconds]);

  const apiError = (requestError) => {
    const data = requestError.response?.data;
    if (typeof data?.detail === "string") return data.detail;
    if (data && typeof data === "object") return Object.values(data).flat().join(" ");
    return "No pudimos completar la solicitud. Inténtalo de nuevo.";
  };

  const requestCode = async (event) => {
    event.preventDefault();
    setLoading(true); setError("");
    try {
      await authService.requestPasswordReset(email);
      setStep("code"); setSeconds(60);
      setMessage("Revisa tu correo. El código tiene una vigencia de 10 minutos.");
    } catch (requestError) { setError(apiError(requestError)); }
    finally { setLoading(false); }
  };

  const updateCode = (index, value) => {
    const digit = value.replace(/\D/g, "").slice(-1);
    const next = [...code]; next[index] = digit; setCode(next); setError("");
    if (digit && index < 5) codeRefs.current[index + 1]?.focus();
  };

  const handleCodeKey = (index, event) => {
    if (event.key === "Backspace" && !code[index] && index > 0) codeRefs.current[index - 1]?.focus();
    if (event.key === "ArrowLeft" && index > 0) codeRefs.current[index - 1]?.focus();
    if (event.key === "ArrowRight" && index < 5) codeRefs.current[index + 1]?.focus();
  };

  const verifyCode = async (event) => {
    event.preventDefault();
    setLoading(true); setError("");
    try {
      await authService.verifyPasswordReset({ email, code: code.join("") });
      setStep("password"); setMessage("Código correcto. Define tu nueva contraseña.");
    } catch (requestError) { setError(apiError(requestError)); }
    finally { setLoading(false); }
  };

  const confirmPassword = async (event) => {
    event.preventDefault();
    setLoading(true); setError("");
    try {
      await authService.confirmPasswordReset({ email, code: code.join(""), new_password: password, new_password_confirm: passwordConfirm });
      setStep("success"); setMessage("Tu contraseña fue actualizada correctamente.");
    } catch (requestError) { setError(apiError(requestError)); }
    finally { setLoading(false); }
  };

  const resendCode = async () => {
    if (seconds > 0) return;
    setLoading(true); setError("");
    try { await authService.requestPasswordReset(email); setSeconds(60); setMessage("Enviamos un nuevo código a tu correo."); }
    catch (requestError) { setError(apiError(requestError)); }
    finally { setLoading(false); }
  };

  if (step === "success") return (
    <div className="recovery-content recovery-success">
      <span className="recovery-success-icon"><ShieldCheck size={28} /></span>
      <span className="auth-card-kicker">Todo listo</span>
      <h2>Contraseña actualizada</h2>
      <p className="muted">Ya puedes volver a entrar al centro de control de tus cultivos.</p>
      <button className="btn btn-primary auth-submit" onClick={onBack}>Volver al inicio <span>→</span></button>
    </div>
  );

  return (
    <div className="recovery-content">
      <button type="button" className="recovery-back" onClick={onBack}>← Volver al inicio</button>
      <span className="recovery-icon"><LockKeyhole size={21} /></span>
      <span className="auth-card-kicker">Recuperación segura</span>
      <h2>{step === "email" ? "Recupera tu acceso" : step === "code" ? "Verifica tu identidad" : "Crea una nueva clave"}</h2>
      <p className="muted">
        {step === "email" && "Te enviaremos un código de 6 dígitos a tu correo registrado."}
        {step === "code" && <>Ingresa el código enviado a <strong>{email}</strong>.</>}
        {step === "password" && "Usa una contraseña segura para proteger tu cuenta."}
      </p>
      <div className="recovery-progress"><i className={step !== "email" ? "active" : ""} /><i className={step === "password" ? "active" : ""} /><i className={step === "success" ? "active" : ""} /></div>

      {step === "email" && <form className="form-grid recovery-form" onSubmit={requestCode}>
        <label className="auth-field"><span>Correo electrónico</span><input type="email" required autoFocus value={email} onChange={(event) => setEmail(event.target.value)} placeholder="tu.correo@ejemplo.com" /></label>
        <button className="btn btn-primary auth-submit" disabled={loading}>{loading ? "Enviando código…" : "Enviar código"}<span>→</span></button>
      </form>}

      {step === "code" && <form className="form-grid recovery-form" onSubmit={verifyCode}>
        <div className="otp-inputs" aria-label="Código de verificación">
          {code.map((digit, index) => <input key={index} ref={(element) => { codeRefs.current[index] = element; }} inputMode="numeric" maxLength={1} value={digit} onChange={(event) => updateCode(index, event.target.value)} onKeyDown={(event) => handleCodeKey(index, event)} autoFocus={index === 0} aria-label={`Dígito ${index + 1}`} />)}
        </div>
        <button className="btn btn-primary auth-submit" disabled={loading || code.join("").length !== 6}>{loading ? "Verificando…" : "Verificar código"}<span>→</span></button>
        <p className="resend-code">¿No recibiste el código? <button type="button" onClick={resendCode} disabled={seconds > 0 || loading}>{seconds > 0 ? `Reenviar en ${seconds}s` : "Reenviar código"}</button></p>
      </form>}

      {step === "password" && <form className="form-grid recovery-form" onSubmit={confirmPassword}>
        <label className="auth-field"><span>Nueva contraseña</span><input type="password" required minLength={8} autoFocus value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Mínimo 8 caracteres" /></label>
        <label className="auth-field"><span>Confirmar contraseña</span><input type="password" required minLength={8} value={passwordConfirm} onChange={(event) => setPasswordConfirm(event.target.value)} placeholder="Repite tu contraseña" /></label>
        <button className="btn btn-primary auth-submit" disabled={loading}>{loading ? "Actualizando…" : "Guardar contraseña"}<span>→</span></button>
      </form>}
      {message && <p className="recovery-message"><ShieldCheck size={14} /> {message}</p>}
      {error && <p className="form-error"><LockKeyhole size={14} /> {error}</p>}
    </div>
  );
}

export default function LoginPage() {
  const { login, loading, error, isAuthenticated } = useAuthStore();
  const [form, setForm] = useState({ username: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [focusedField, setFocusedField] = useState("");
  const [theme, setTheme] = useState(() => localStorage.getItem("siaac-login-theme") || "dark");
  const [showRecovery, setShowRecovery] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [registrationMessage, setRegistrationMessage] = useState("");
  const [emailVerification, setEmailVerification] = useState(null);
  const [twoFactorChallenge, setTwoFactorChallenge] = useState(null);

  useEffect(() => {
    localStorage.setItem("siaac-login-theme", theme);
  }, [theme]);

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  const handleSubmit = async (event) => {
    event.preventDefault();
    const result = await login(form.username, form.password);
    if (result?.requiresTwoFactor) setTwoFactorChallenge(result);
  };

  return (
    <div className={`auth-screen theme-${theme}`}>
      <section className="auth-visual">
        <div className="visual-orbit orbit-large" />
        <div className="visual-orbit orbit-small" />
        <div className="auth-visual-header">
          <LogoSiaac />
          <button type="button" className="theme-toggle visual-theme-toggle" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label={`Cambiar a tema ${theme === "dark" ? "claro" : "oscuro"}`}>
            {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
          </button>
        </div>
        <div className="auth-visual-copy">
          <span className="eyebrow"><ShieldCheck size={14} /> plataforma protegida</span>
          <h1 className="siaac-name" aria-label="SIAAC">
            {["S", "I", "A", "A", "C"].map((letter, index) => <span key={`${letter}-${index}`}>{letter}</span>)}
          </h1>
          <p className="siaac-tagline">Sistema Inteligente de Agricultura Asistida por Computadora</p>
          <h2>Cuida lo que<br /><em>cultivas</em></h2>
          <p>Inteligencia artificial para detectar animales y proteger cada zona de tu cultivo.</p>
          <div className="visual-features">
            <span><Sprout size={15} /> cultivos vigilados</span>
            <span><Radio size={15} /> monitoreo en vivo</span>
          </div>
        </div>
        <div className="auth-visual-bottom">
          <span className="status-led" /> sistema SIAAC operativo
          <strong>01 <small>/ 03</small></strong>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-card">
          <div className="mobile-auth-brand">
            <LogoSiaac />
            <div><strong>SIAAC</strong><small>vigilancia inteligente</small></div>
          </div>
          <button type="button" className="theme-toggle card-theme-toggle" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label={`Cambiar a tema ${theme === "dark" ? "claro" : "oscuro"}`}>
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          <BuhoVigilante passwordFocused={focusedField === "password"} usernameFocused={focusedField === "username"} />
          {twoFactorChallenge ? <SegundoFactor challenge={twoFactorChallenge} onBack={() => setTwoFactorChallenge(null)} /> : emailVerification ? <VerificacionCorreo email={emailVerification.email} username={emailVerification.username} onBack={() => setEmailVerification(null)} onVerified={(username) => { setEmailVerification(null); setRegistrationMessage("Correo verificado. Ya puedes iniciar sesión."); setForm((current) => ({ ...current, username, password: "" })); }} /> : showRecovery ? <RecuperacionPassword onBack={() => setShowRecovery(false)} /> : showRegister ? <RegistroUsuario onBack={() => setShowRegister(false)} onRegistered={(username, email) => { setShowRegister(false); setEmailVerification({ username, email }); }} /> : <>
          <div className="auth-card-heading">
            <span className="auth-card-kicker">Bienvenido a SIAAC</span>
            <h2>Inicia tu vigilancia</h2>
            <p className="muted">Accede al centro de control de tus cultivos.</p>
          </div>

          <form onSubmit={handleSubmit} className="form-grid">
            <label className={`auth-field ${focusedField === "username" ? "is-focused" : ""}`}>
              <span>Usuario</span>
              <input
                autoFocus
                required
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                onFocus={() => setFocusedField("username")}
                onBlur={() => setFocusedField("")}
                placeholder="tu.usuario"
              />
            </label>
            <label className={`auth-field ${focusedField === "password" ? "is-focused" : ""}`}>
              <span>Contraseña</span>
              <div className="password-input-wrap">
              <input
                required
                type={showPassword ? "text" : "password"}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                onFocus={() => setFocusedField("password")}
                onBlur={() => setFocusedField("")}
                placeholder="••••••••"
              />
                <button type="button" className="password-toggle" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}>
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </label>
            <div className="auth-options">
              <label className="remember-option"><input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} /><span>Recordarme</span></label>
              <button type="button" className="forgot-button" onClick={() => setShowRecovery(true)}>¿Olvidaste tu contraseña?</button>
            </div>
            {registrationMessage && <p className="recovery-message"><ShieldCheck size={14} /> {registrationMessage}</p>}
            {error && <p className="form-error"><LockKeyhole size={15} /> {error}</p>}
            <button className="btn btn-primary auth-submit" disabled={loading}>
              {loading ? "Validando acceso…" : "Entrar al sistema"}
              {!loading && <span>→</span>}
            </button>
          </form>

          <p className="auth-foot">Acceso exclusivo para usuarios autorizados</p>
          <button type="button" className="register-link" onClick={() => { setRegistrationMessage(""); setShowRegister(true); }}>¿Aún no tienes una cuenta? <strong>Regístrate</strong></button>
          </>}
        </div>
      </section>
    </div>
  );
}
