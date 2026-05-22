"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { LayoutDashboard, Plus, LogOut, Loader2, UserCircle, Lock } from "lucide-react";

const TIER_BADGE: Record<string, { label: string; cls: string }> = {
  free:  { label: "Free",  cls: "bg-slate-100 text-slate-500" },
  basic: { label: "Basic", cls: "bg-violet-100 text-violet-700" },
  pro:   { label: "Pro",   cls: "bg-amber-100 text-amber-700" },
};

function NavLink({
  href, icon: Icon, children, active,
}: {
  href: string;
  icon: React.ElementType;
  children: React.ReactNode;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
        active
          ? "bg-violet-50 text-violet-700 font-medium"
          : "text-slate-700 hover:bg-slate-50 hover:text-violet-700"
      }`}
    >
      <Icon className="w-4 h-4 shrink-0" />
      {children}
    </Link>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

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

  const tier = user.subscription_tier;
  const badge = TIER_BADGE[tier] ?? TIER_BADGE.free;
  const isFree = tier === "free";

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r border-slate-200 flex flex-col shrink-0">
        <div className="px-5 py-4 border-b border-slate-100">
          <Link href="/" className="font-bold text-violet-700 text-lg">✦ Tech Zi Wei</Link>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          <NavLink href="/dashboard" icon={LayoutDashboard} active={pathname === "/dashboard"}>
            My Charts
          </NavLink>
          <NavLink href="/dashboard/new" icon={Plus} active={pathname === "/dashboard/new"}>
            New Chart
          </NavLink>
          <NavLink href="/dashboard/account" icon={UserCircle} active={pathname === "/dashboard/account"}>
            Account
          </NavLink>
        </nav>

        {/* Upgrade nudge for free users */}
        {isFree && (
          <div className="mx-3 mb-3 p-3 bg-violet-50 border border-violet-100 rounded-xl">
            <p className="text-xs text-violet-700 font-medium flex items-center gap-1 mb-1.5">
              <Lock className="w-3 h-3" /> Unlock readings
            </p>
            <p className="text-xs text-violet-600 leading-snug mb-2">
              Get AI-generated psychological insights for all your charts.
            </p>
            <Link
              href="/dashboard/account"
              className="block text-center text-xs bg-violet-600 hover:bg-violet-500 text-white font-medium px-3 py-1.5 rounded-lg transition-colors"
            >
              Unlock — $9.99
            </Link>
          </div>
        )}

        <div className="px-3 pb-4 border-t border-slate-100 pt-3 space-y-1">
          <div className="flex items-center gap-2 px-3 mb-1">
            <p className="text-xs text-slate-400 truncate flex-1">{user.email}</p>
            <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full shrink-0 ${badge.cls}`}>
              {badge.label}
            </span>
          </div>
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
