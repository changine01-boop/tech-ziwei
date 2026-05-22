"use client";

import {
  createContext, useCallback, useContext, useEffect, useState, type ReactNode,
} from "react";
import { api } from "@/lib/api";
import type { UserResponse } from "@/lib/types";

interface AuthContextValue {
  user: UserResponse | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const tok = localStorage.getItem("tz_token");
    if (!tok) { setLoading(false); return; }
    api.users.me()
      .then(setUser)
      .catch(() => localStorage.removeItem("tz_token"))
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    await api.auth.login(email, password);
    const me = await api.users.me();
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    api.auth.logout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
