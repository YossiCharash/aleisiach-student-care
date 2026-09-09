import type { ReactNode } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "@/components/layout/Sidebar";

export function AppShell(): ReactNode {
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <main className="min-w-0 flex-1 px-10 py-8">
        <div className="mx-auto w-full max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
