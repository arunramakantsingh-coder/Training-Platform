const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "";
const API_PREFIX = "/api/v1";

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const requestPath = path.startsWith("/api/") ? path : `${API_PREFIX}${path}`;
  const response = await fetch(`${API_BASE_URL}${requestPath}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
    cache: "no-store",
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed with status ${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
