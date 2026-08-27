import type { ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogOut, Settings, UserCog } from "lucide-react";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { roleLabels } from "@/lib/utils/hebrew";
import { Button } from "@/components/ui/Button";

export function Header(): ReactNode {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout(): Promise<void> {
    await logout();
    navigate("/login", { replace: true });
  }

  if (!user) {
    return null;
  }

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-xl font-bold text-brand">עלי שיח</span>
          <span className="hidden text-sm text-ink-muted sm:inline">
            מערכת ניהול תלמידים
          </span>
        </Link>

        <div className="flex items-center gap-3">
          <div className="text-end">
            <div className="text-sm font-medium text-ink">{user.full_name}</div>
            <div className="text-xs text-ink-muted">{roleLabels[user.role]}</div>
          </div>

          {permissions.canManage(user) && (
            <Button asChild variant="ghost" size="icon" title="הגדרות">
              <Link to="/settings">
                <Settings className="h-5 w-5" />
              </Link>
            </Button>
          )}

          <Button asChild variant="ghost" size="icon" title="הגדרות אישיות">
            <Link to="/settings/personal">
              <UserCog className="h-5 w-5" />
            </Link>
          </Button>

          <Button variant="outline" size="sm" onClick={handleLogout}>
            <LogOut className="h-4 w-4" />
            יציאה
          </Button>
        </div>
      </div>
    </header>
  );
}
