import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { FullPageSpinner } from "./components/common/Primitives";
import { useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import ProjectDetail from "./pages/ProjectDetail";
import Tasks from "./pages/Tasks";
import KanbanBoard from "./pages/KanbanBoard";
import CalendarView from "./pages/CalendarView";
import Reports from "./pages/Reports";
import TeamManagement from "./pages/TeamManagement";
import Settings from "./pages/Settings";
import AuditLog from "./pages/AuditLog";
import NotFound from "./pages/NotFound";

export default function App() {
  const { loading } = useAuth();
  if (loading) return <FullPageSpinner />;

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/projects/:projectId" element={<ProjectDetail />} />
        <Route path="/projects/:projectId/board" element={<KanbanBoard />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/calendar" element={<CalendarView />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/team" element={<TeamManagement />} />
        <Route path="/settings" element={<Settings />} />
        <Route
          path="/audit-log"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AuditLog />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
