"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { LayoutDashboard, Plus, LogOut, Loader2 } from "lucide-react";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-violet-500" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r border-slate-200 flex flex-col shrink-0">
        <div className="px-5 py-4 border-b border-slate-100">
          <Link href="/" className="font-bold text-violet-700 text-lg">✦ Tech Zi Wei</Link>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          <Link
            href="/dashboard"
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-slate-700 hover:bg-slate-50 hover:text-violet-700 transition-colors"
          >
            <LayoutDashboard className="w-4 h-4" /> My Charts
          </Link>
          <Link
            href="/dashboard/new"
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-slate-700 hover:bg-slate-50 hover:text-violet-700 transition-colors"
          >
            <Plus className="w-4 h-4" /> New Chart
          </Link>
        </nav>
        <div className="px-3 pb-4 border-t border-slate-100 pt-3">
          <p className="text-xs text-slate-400 px-3 mb-2 truncate">{user.email}</p>
          <button
            onClick={() => { logout(); router.push("/"); }}
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-slate-500 hover:text-red-500 hover:bg-red-50 transition-colors w-full"
          >
            <LogOut className="w-4 h-4" /> Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-8">{children}</main>
    </div>
  );
}
