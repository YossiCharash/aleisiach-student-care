import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { ManagerRoute, ProtectedRoute } from "@/components/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import { LoginPage } from "@/pages/LoginPage";
import { ForgotPasswordPage } from "@/pages/ForgotPasswordPage";
import { ResetPasswordPage } from "@/pages/ResetPasswordPage";
import { AcceptInvitationPage } from "@/pages/AcceptInvitationPage";
import { StudentsPage } from "@/pages/StudentsPage";
import { ArchivedStudentsPage } from "@/pages/ArchivedStudentsPage";
import { StudentPage } from "@/pages/StudentPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { PersonalSettingsPage } from "@/pages/PersonalSettingsPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

export function AppRoutes(): ReactNode {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/accept-invitation" element={<AcceptInvitationPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="/" element={<StudentsPage />} />
          <Route path="/students/:studentId" element={<StudentPage />} />
          <Route path="/settings/personal" element={<PersonalSettingsPage />} />
          <Route element={<ManagerRoute />}>
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/students/archived" element={<ArchivedStudentsPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
}
