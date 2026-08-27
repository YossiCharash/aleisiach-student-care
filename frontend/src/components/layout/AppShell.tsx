import type { ReactNode } from "react";
import { Outlet } from "react-router-dom";
import { Header } from "@/components/layout/Header";

export function AppShell(): ReactNode {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
