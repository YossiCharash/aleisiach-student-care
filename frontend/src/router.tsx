import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import {
  InstitutionRoute,
  ManagerRoute,
  ProtectedRoute,
  SuperAdminRoute,
} from "@/components/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import { LoginPage } from "@/pages/LoginPage";
import { ForgotPasswordPage } from "@/pages/ForgotPasswordPage";
import { ResetPasswordPage } from "@/pages/ResetPasswordPage";
import { AcceptInvitationPage } from "@/pages/AcceptInvitationPage";
import { HomePage } from "@/pages/HomePage";
import { StudentsPage } from "@/pages/StudentsPage";
import { ArchivedStudentsPage } from "@/pages/ArchivedStudentsPage";
import { StudentPage } from "@/pages/StudentPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { InstitutionsPage } from "@/pages/InstitutionsPage";
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
          <Route path="/settings" element={<SettingsPage />} />
          <Route
            path="/settings/personal"
            element={<Navigate to="/settings?tab=account" replace />}
          />
          <Route element={<SuperAdminRoute />}>
            <Route path="/institutions" element={<InstitutionsPage />} />
          </Route>
          <Route element={<InstitutionRoute />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/students" element={<StudentsPage />} />
            <Route path="/students/:studentId" element={<StudentPage />} />
            <Route element={<ManagerRoute />}>
              <Route path="/students/archived" element={<ArchivedStudentsPage />} />
            </Route>
          </Route>
        </Route>
      </Route>

      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
}
