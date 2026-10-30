import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "../components/layout/AppLayout";
import { useAuthStore } from "../store/authStore";

import LoginPage from "../modules/autenticacion/pages/LoginPage";
import ProfilePage from "../modules/autenticacion/pages/ProfilePage";
import DashboardPage from "../modules/reportes/pages/DashboardPage";
import ReportsPage from "../modules/reportes/pages/ReportsPage";
import CropsPage from "../modules/cultivos/pages/CropsPage";
import ZonesPage from "../modules/cultivos/pages/ZonesPage";
import MonitoringPage from "../modules/monitoreo/pages/MonitoringPage";
import DetectionPage from "../modules/deteccion/pages/DetectionPage";
import DevicesPage from "../modules/deteccion/pages/DevicesPage";
import DisuasionPage from "../modules/respuestas/pages/DisuasionPage";
import NotificationsPage from "../modules/notificaciones/pages/NotificationsPage";

function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/crops" element={<CropsPage />} />
        <Route path="/zones" element={<ZonesPage />} />
        <Route path="/monitoring" element={<MonitoringPage />} />
        <Route path="/detection" element={<DetectionPage />} />
        <Route path="/devices" element={<DevicesPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/disuasion" element={<DisuasionPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
