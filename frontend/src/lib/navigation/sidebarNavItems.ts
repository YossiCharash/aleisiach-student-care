import { Archive, Building2, Settings, Users, type LucideIcon } from "lucide-react";
import type { UserResponse } from "@/lib/api/types";

export interface SidebarNavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  isActive: (pathname: string) => boolean;
}

const ARCHIVED_STUDENTS_PATH = "/students/archived";

const students: SidebarNavItem = {
  to: "/students",
  label: "תלמידים",
  icon: Users,
  isActive: (pathname) =>
    pathname === "/" ||
    (pathname.startsWith("/students") && !pathname.startsWith(ARCHIVED_STUDENTS_PATH)),
};

const archivedStudents: SidebarNavItem = {
  to: ARCHIVED_STUDENTS_PATH,
  label: "ארכיון תלמידים",
  icon: Archive,
  isActive: (pathname) => pathname.startsWith(ARCHIVED_STUDENTS_PATH),
};

const institutions: SidebarNavItem = {
  to: "/institutions",
  label: "מוסדות",
  icon: Building2,
  isActive: (pathname) => pathname.startsWith("/institutions"),
};

const settings: SidebarNavItem = {
  to: "/settings",
  label: "הגדרות",
  icon: Settings,
  isActive: (pathname) => pathname.startsWith("/settings"),
};

export function sidebarNavItems(user: UserResponse): SidebarNavItem[] {
  if (user.role === "super_admin") {
    return [institutions, settings];
  }
  if (user.role === "manager") {
    return [students, archivedStudents, settings];
  }
  return [students, settings];
}
