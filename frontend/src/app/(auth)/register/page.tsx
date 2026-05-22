"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    try {
      await api.auth.register(email, password);
      await login(email, password);
      router.push("/dashboard/new");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-sm">
      <h1 className="text-2xl font-bold text-white mb-2">Create your account</h1>
      <p className="text-slate-400 mb-8">Generate your first chart in minutes</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-900/40 border border-red-700 text-red-300 text-sm rounded-lg px-4 py-3">
            {error}
          </div>
        )}
        <div>
          <label className="block text-sm text-slate-300 mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label className="block text-sm text-slate-300 mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
            placeholder="Min. 8 characters"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg transition-colors"
        >
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="mt-6 text-center text-slate-400 text-sm">
        Already have an account?{" "}
        <Link href="/login" className="text-violet-400 hover:text-violet-300">
          Sign in
        </Link>
      </p>
    </div>
  );
}
