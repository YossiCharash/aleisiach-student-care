import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { AuthProvider, useAuth } from "@/lib/auth/AuthContext";
import { notifyUnauthorized } from "@/lib/auth/sessionEvents";

vi.mock("@/lib/api/endpoints", () => ({
  authApi: { logout: vi.fn().mockResolvedValue(undefined) },
}));

function setup(): {
  client: QueryClient;
  wrapper: (p: { children: ReactNode }) => ReactNode;
} {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  client.setQueryData(["students"], [{ id: "s1", full_name: "תלמיד של המשתמש הקודם" }]);
  function wrapper({ children }: { children: ReactNode }): ReactNode {
    return (
      <QueryClientProvider client={client}>
        <AuthProvider>{children}</AuthProvider>
      </QueryClientProvider>
    );
  }
  return { client, wrapper };
}

describe("session isolation", () => {
  beforeEach(() => localStorage.clear());

  it("drops cached data on logout so the next user cannot see it", async () => {
    const { client, wrapper } = setup();
    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(client.getQueryData(["students"])).toBeDefined();

    await act(async () => {
      await result.current.logout();
    });

    expect(client.getQueryData(["students"])).toBeUndefined();
  });

  it("drops cached data when the session is rejected as unauthorized", async () => {
    const { client, wrapper } = setup();
    renderHook(() => useAuth(), { wrapper });

    act(() => notifyUnauthorized());

    await waitFor(() => expect(client.getQueryData(["students"])).toBeUndefined());
  });
});
