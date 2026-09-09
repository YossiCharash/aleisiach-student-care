import type { ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";
import { useAuth } from "@/lib/auth/AuthContext";
import { displayName } from "@/lib/auth/displayName";
import { homePath } from "@/lib/auth/homePath";
import { sidebarNavItems } from "@/lib/navigation/sidebarNavItems";
import { roleLabels } from "@/lib/utils/hebrew";
import { initials } from "@/lib/utils/initials";
import { cn } from "@/lib/utils/cn";
import { Button } from "@/components/ui/Button";

export function Sidebar(): ReactNode {
  const { user, institutionName, logout } = useAuth();
  const { pathname } = useLocation();
  const navigate = useNavigate();

  async function handleLogout(): Promise<void> {
    await logout();
    navigate("/login", { replace: true });
  }

  if (!user) {
    return null;
  }

  const subtitle =
    user.role === "super_admin"
      ? "ניהול מוסדות"
      : (institutionName ?? "מערכת ניהול תלמידים");

  return (
    <aside className="flex w-64 shrink-0 flex-col border-e border-slate-200 bg-white px-5 py-6">
      <Link to={homePath(user)} className="flex items-center gap-3 px-1 pb-6">
        <img src="/logo.png" alt="עלי שיח" className="h-10 w-auto" />
        <span className="text-sm text-ink-muted">{subtitle}</span>
      </Link>

      <nav className="flex flex-col gap-1">
        {sidebarNavItems(user).map((item) => {
          const active = item.isActive(pathname);
          const Icon = item.icon;
          return (
            <Link
              key={item.to}
              to={item.to}
              aria-current={active ? "page" : undefined}
              className={cn(
                "relative flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm transition-colors",
                active
                  ? "bg-brand-50 font-semibold text-brand-700"
                  : "font-medium text-ink-muted hover:bg-slate-50 hover:text-ink"
              )}
            >
              {active && (
                <span
                  className="absolute inset-y-2 start-0 w-0.5 rounded-full bg-brand"
                  aria-hidden
                />
              )}
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto flex items-center gap-3 border-t border-slate-100 pt-4">
        <span
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand text-sm font-bold text-white"
          aria-hidden
        >
          {initials(user.full_name)}
        </span>
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-medium text-ink">{displayName(user)}</div>
          <div className="text-xs text-ink-muted">{roleLabels[user.role]}</div>
        </div>
        <Button variant="ghost" size="icon" title="יציאה" onClick={handleLogout}>
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </aside>
  );
}
