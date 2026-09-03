import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

export function HomePage(): ReactNode {
  return <Navigate to="/students" replace />;
}
