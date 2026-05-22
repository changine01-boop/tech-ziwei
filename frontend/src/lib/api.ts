import type {
  ChartRequest, ChartResponse, CheckoutSessionResponse,
  PreviewRequest, PreviewResponse,
  ReadingResponse, ReadingType,
  TokenResponse, UserResponse,
} from "./types";
import { NetworkError, PaymentRequiredError, RateLimitError } from "./errors";

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

  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, { ...options, headers });
  } catch (e) {
    if (e instanceof TypeError) {
      throw new NetworkError();
    }
    throw e;
  }

  if (res.status === 401) {
    localStorage.removeItem("tz_token");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (res.status === 402) {
    throw new PaymentRequiredError();
  }

  if (res.status === 429) {
    throw new RateLimitError();
  }

  if (res.status >= 500) {
    throw new Error("Server error — please try again.");
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
    delete: (id: string) =>
      request<void>(`/charts/${id}`, { method: "DELETE" }),
    downloadPdf: async (chartId: string): Promise<void> => {
      const tok = token();
      const res = await fetch(`${BASE}/charts/${chartId}/pdf`, {
        headers: tok ? { Authorization: `Bearer ${tok}` } : {},
      });
      if (!res.ok) throw new Error("Download failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ziwei-${chartId.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
  },

  readings: {
    request: (chartId: string, type: ReadingType) =>
      request<ReadingResponse>(`/charts/${chartId}/report?reading_type=${type}`, {
        method: "POST",
      }),
    get: (chartId: string, type: ReadingType) =>
      request<ReadingResponse>(`/charts/${chartId}/readings/${type}`),
  },

  payments: {
    createCheckoutSession: () =>
      request<CheckoutSessionResponse>("/payments/checkout-session", { method: "POST" }),
  },

  preview: {
    calculate: (payload: PreviewRequest) =>
      request<PreviewResponse>("/preview", { method: "POST", body: JSON.stringify(payload) }),
  },
};
