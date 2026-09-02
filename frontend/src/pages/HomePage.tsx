import type { ReactNode } from "react";
import { Link, Navigate } from "react-router-dom";
import { Archive, Settings, Users } from "lucide-react";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { Card } from "@/components/ui/Card";

interface Destination {
  to: string;
  title: string;
  description: string;
  icon: ReactNode;
}

export function HomePage(): ReactNode {
  const { user } = useAuth();

  if (!user) {
    return null;
  }
  if (!permissions.canManage(user)) {
    return <Navigate to="/students" replace />;
  }

  const destinations: Destination[] = [
    {
      to: "/students",
      title: "תלמידים",
      description: "רשימת התלמידים לפי כיתות",
      icon: <Users className="h-7 w-7" />,
    },
    {
      to: "/settings",
      title: "הגדרות",
      description: "משתמשים · כיתות · כישורים · אבחונים",
      icon: <Settings className="h-7 w-7" />,
    },
    {
      to: "/students/archived",
      title: "ארכיון",
      description: "תלמידים שהועברו לארכיון",
      icon: <Archive className="h-7 w-7" />,
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-ink">שלום {user.full_name}</h1>
      <p className="mt-1 text-sm text-ink-muted">במה תרצו להתחיל?</p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {destinations.map((destination) => (
          <Link key={destination.to} to={destination.to} className="group">
            <Card className="flex h-full items-start gap-4 p-6 transition-colors group-hover:border-brand-300 group-hover:bg-brand-50/40">
              <span className="rounded-lg bg-brand-50 p-3 text-brand">
                {destination.icon}
              </span>
              <span>
                <span className="block text-lg font-semibold text-ink">
                  {destination.title}
                </span>
                <span className="mt-1 block text-sm text-ink-muted">
                  {destination.description}
                </span>
              </span>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
