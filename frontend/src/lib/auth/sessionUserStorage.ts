import type { UserResponse } from "@/lib/api/types";

const USER_KEY = "aleisiach.session.user";

export function getStoredUser(): UserResponse | null {
  try {
    const raw = window.localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as UserResponse) : null;
  } catch {
    return null;
  }
}

export function setStoredUser(user: UserResponse): void {
  try {
    window.localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch {
    // Storage unavailable; the in-memory context still holds the user for this tab.
  }
}

export function clearStoredUser(): void {
  try {
    window.localStorage.removeItem(USER_KEY);
  } catch {
    // Nothing to clear if storage is unavailable.
  }
}
