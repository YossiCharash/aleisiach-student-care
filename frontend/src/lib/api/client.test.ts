import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiClient } from "@/lib/api/client";
import { getToken, setToken } from "@/lib/auth/tokenStorage";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("apiClient", () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("parses a JSON success body", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(jsonResponse({ value: 42 }));
    const result = await apiClient.get<{ value: number }>("/thing");
    expect(result).toEqual({ value: 42 });
  });

  it("attaches the bearer token on authenticated requests", async () => {
    setToken("secret-token");
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(jsonResponse({}));
    await apiClient.get("/secure");
    const headers = (fetchMock.mock.calls[0][1]?.headers ?? {}) as Record<string, string>;
    expect(headers["Authorization"]).toBe("Bearer secret-token");
  });

  it("throws ApiError carrying the backend code and message", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse({ code: "not_found", message: "לא נמצא" }, 404)
    );
    await expect(apiClient.get("/missing")).rejects.toMatchObject({
      status: 404,
      code: "not_found",
      message: "לא נמצא",
    });
  });

  it("clears the token on a 401 response", async () => {
    setToken("expired");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse({ message: "unauthorized" }, 401)
    );
    await expect(apiClient.get("/secure")).rejects.toBeInstanceOf(ApiError);
    expect(getToken()).toBeNull();
  });

  it("returns undefined for a 204 response", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(null, { status: 204 }));
    const result = await apiClient.post("/logout");
    expect(result).toBeUndefined();
  });
});
