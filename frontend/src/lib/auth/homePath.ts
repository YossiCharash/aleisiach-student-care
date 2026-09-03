import type { UserResponse } from "@/lib/api/types";

export function homePath(user: UserResponse | null): string {
  return user?.role === "super_admin" ? "/institutions" : "/";
}
