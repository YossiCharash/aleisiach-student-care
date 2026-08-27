import { getToken, clearToken } from "@/lib/auth/tokenStorage";
import { notifyUnauthorized } from "@/lib/auth/sessionEvents";

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "/api";

export class ApiError extends Error {
  readonly status: number;
  readonly code: string | null;

  constructor(status: number, code: string | null, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  auth?: boolean;
  signal?: AbortSignal;
}

async function parseErrorMessage(response: Response): Promise<{ code: string | null; message: string }> {
  try {
    const payload = (await response.json()) as { code?: string; message?: string; error?: string };
    return {
      code: payload.code ?? null,
      message: payload.message ?? payload.error ?? response.statusText,
    };
  } catch {
    return { code: null, message: response.statusText };
  }
}

async function request<TResponse>(path: string, options: RequestOptions = {}): Promise<TResponse> {
  const { method = "GET", body, auth = true, signal } = options;
  const headers: Record<string, string> = {};

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (auth) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    signal,
  });

  if (response.status === 401 && auth) {
    clearToken();
    notifyUnauthorized();
  }

  if (!response.ok) {
    const { code, message } = await parseErrorMessage(response);
    throw new ApiError(response.status, code, message);
  }

  if (response.status === 204) {
    return undefined as TResponse;
  }

  const contentType = response.headers.get("Content-Type") ?? "";
  if (!contentType.includes("application/json")) {
    return (await response.blob()) as TResponse;
  }

  return (await response.json()) as TResponse;
}

export function buildPdfUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export const apiClient = {
  get: <TResponse>(path: string, signal?: AbortSignal): Promise<TResponse> =>
    request<TResponse>(path, { method: "GET", signal }),
  post: <TResponse>(path: string, body?: unknown): Promise<TResponse> =>
    request<TResponse>(path, { method: "POST", body }),
  put: <TResponse>(path: string, body?: unknown): Promise<TResponse> =>
    request<TResponse>(path, { method: "PUT", body }),
  patch: <TResponse>(path: string, body?: unknown): Promise<TResponse> =>
    request<TResponse>(path, { method: "PATCH", body }),
  postPublic: <TResponse>(path: string, body?: unknown): Promise<TResponse> =>
    request<TResponse>(path, { method: "POST", body, auth: false }),
};
