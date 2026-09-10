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
    await Promise.resolve(logout()).catch(() => undefined);
    navigate("/login", { replace: true });
  }

  if (!user) {
    return null;
  }

  const subtitle =
    user.role === "super_admin"
      ? "ניהול מוסדות"
      : (institutionName ?? "מערכת ניהול חניכים");

  return (
    <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col self-start overflow-y-auto border-e border-slate-200/80 bg-surface-raised/85 px-4 py-6 backdrop-blur-sm">
      <Link
        to={homePath(user)}
        className="mb-6 flex flex-col gap-2.5 rounded-card border border-slate-200/70 bg-white px-3.5 py-3 shadow-soft"
      >
        <img src="/logo.png" alt="עלי שיח" className="h-9 w-auto" />
        <span className="flex items-center gap-1.5 border-t border-slate-100 pt-2 text-xs font-medium text-ink-soft">
          <span className="leaf-tick !h-3 !w-1" aria-hidden />
          {subtitle}
        </span>
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
                "group relative flex items-center gap-3 rounded-control px-3.5 py-2.5 text-sm transition-all duration-150",
                active
                  ? "bg-brand-soft font-semibold text-brand-700 shadow-soft"
                  : "font-medium text-ink-muted hover:bg-slate-100/70 hover:text-ink"
              )}
            >
              {active && (
                <span
                  className="absolute inset-y-2.5 start-0 w-1 rounded-full bg-brand"
                  aria-hidden
                />
              )}
              <Icon
                className={cn(
                  "h-5 w-5 shrink-0 transition-colors",
                  active ? "text-brand-600" : "text-ink-soft group-hover:text-ink-muted"
                )}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto flex items-center gap-3 rounded-card border border-slate-200/70 bg-white/60 p-2.5 shadow-soft">
        <span
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand text-sm font-bold text-white shadow-brand-sm"
          aria-hidden
        >
          {initials(user.full_name)}
        </span>
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-semibold text-ink">
            {displayName(user)}
          </div>
          <div className="text-xs text-ink-soft">{roleLabels[user.role]}</div>
        </div>
        <Button variant="ghost" size="icon" title="יציאה" onClick={handleLogout}>
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </aside>
  );
}
