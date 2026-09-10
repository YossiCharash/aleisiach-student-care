import type { ReactNode } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "@/components/layout/Sidebar";

export function AppShell(): ReactNode {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="min-w-0 flex-1 px-10 py-9">
        <div className="mx-auto w-full max-w-7xl animate-fade-up">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
