import type {
  ChartRequest, ChartResponse, ReadingResponse, ReadingType,
  TokenResponse, UserResponse,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function token(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("tz_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const tok = token();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (tok) headers["Authorization"] = `Bearer ${tok}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem("tz_token");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────
export const api = {
  auth: {
    register: (email: string, password: string) =>
      request<UserResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    login: async (email: string, password: string): Promise<void> => {
      const data = await request<TokenResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("tz_token", data.access_token);
    },
    logout: () => localStorage.removeItem("tz_token"),
  },

  users: {
    me: () => request<UserResponse>("/users/me"),
  },

  charts: {
    list: () => request<ChartResponse[]>("/charts"),
    get:  (id: string) => request<ChartResponse>(`/charts/${id}`),
    create: (payload: ChartRequest) =>
      request<ChartResponse>("/charts", { method: "POST", body: JSON.stringify(payload) }),
  },

  readings: {
    request: (chartId: string, type: ReadingType) =>
      request<ReadingResponse>(`/charts/${chartId}/report?reading_type=${type}`, {
        method: "POST",
      }),
  },
};
