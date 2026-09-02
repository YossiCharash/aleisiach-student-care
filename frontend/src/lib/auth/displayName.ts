import type { UserResponse } from "@/lib/api/types";

export function displayName(user: UserResponse): string {
  return user.username ?? user.full_name;
}
