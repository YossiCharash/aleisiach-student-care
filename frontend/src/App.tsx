import type { ReactNode } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { createQueryClient } from "@/lib/queryClient";
import { AuthProvider } from "@/lib/auth/AuthContext";
import { AppRoutes } from "@/router";

const queryClient = createQueryClient();

export function App(): ReactNode {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
