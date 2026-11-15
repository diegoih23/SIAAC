import { NavLink } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";
import {
  Camera,
  Cpu,
  LayoutDashboard,
  Leaf,
  Map,
  Radio,
  Siren,
  Sprout,
  Users,
  FileBarChart,
} from "lucide-react";

const sections = [
  {
    title: "Supervisión",
    links: [
      { to: "/dashboard", label: "Tablero", icon: LayoutDashboard },
      { to: "/monitoring", label: "Monitoreo en vivo", icon: Radio },
      { to: "/detection", label: "Detecciones IA", icon: Camera },
    ],
  },
  {
    title: "Gestión",
    links: [
      { to: "/crops", label: "Cultivos", icon: Sprout },
      { to: "/zones", label: "Zonas", icon: Map },
      { to: "/devices", label: "Dispositivos", icon: Cpu },
      { to: "/users", label: "Usuarios y roles", icon: Users },
    ],
  },
  {
    title: "Control",
    links: [
      { to: "/disuasion", label: "Respuesta disuasiva", icon: Siren },
      { to: "/reports", label: "Reportes", icon: FileBarChart },
    ],
  },
];

export default function Sidebar() {
  const isAdmin = useAuthStore((state) => state.user?.role === "ADMIN");
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="brand-icon"><Leaf size={22} /></span>
        <div>
          <strong>SIAAC</strong>
          <small>Agricultura inteligente</small>
        </div>
      </div>

      <nav className="sidebar-nav">
        {sections.map((section) => (
          <div key={section.title} className="nav-section">
            <p className="nav-title">{section.title}</p>
              {section.links.filter(({ to }) => to !== "/users" || isAdmin).map(({ to, label, icon: Icon }) => (
              <NavLink key={to} to={to} className="nav-link">
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-foot">
        <span className="pulse-dot" /> Sistema operativo
      </div>
    </aside>
  );
}
