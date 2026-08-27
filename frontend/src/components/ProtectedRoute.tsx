import type { ReactNode } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/lib/auth/AuthContext";

export function ProtectedRoute(): ReactNode {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}

export function ManagerRoute(): ReactNode {
  const { user } = useAuth();

  if (user?.role !== "manager") {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
