"use client";

import { useEffect, useState } from "react";
import { Loader2, CheckCircle2, Lock, BarChart3, Calendar, Mail } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { ChartResponse } from "@/lib/types";

const TIER_LABELS: Record<string, string> = {
  free:  "Free",
  basic: "Basic",
  pro:   "Pro",
};

const TIER_STYLES: Record<string, string> = {
  free:  "bg-slate-100 text-slate-600",
  basic: "bg-violet-100 text-violet-700",
  pro:   "bg-amber-100 text-amber-700",
};

export default function AccountPage() {
  const { user, refetchUser } = useAuth();
  const [charts, setCharts] = useState<ChartResponse[]>([]);
  const [chartsLoading, setChartsLoading] = useState(true);
  const [upgradeLoading, setUpgradeLoading] = useState(false);
  const [upgradeError, setUpgradeError] = useState("");

  useEffect(() => {
    api.charts.list()
      .then(setCharts)
      .finally(() => setChartsLoading(false));
  }, []);

  async function handleUpgrade() {
    setUpgradeLoading(true);
    setUpgradeError("");
    try {
      const { url } = await api.payments.createCheckoutSession();
      window.location.href = url;
    } catch (e: unknown) {
      setUpgradeError(e instanceof Error ? e.message : "Something went wrong");
      setUpgradeLoading(false);
    }
  }

  if (!user) return null;

  const tier = user.subscription_tier;
  const isFree = tier === "free";
  const memberSince = new Date(user.created_at).toLocaleDateString("en-US", {
    year: "numeric", month: "long", day: "numeric",
  });

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Account</h1>
        <p className="text-slate-500 text-sm mt-1">Manage your subscription and profile</p>
      </div>

      {/* Profile card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">Profile</h2>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-violet-100 rounded-full flex items-center justify-center shrink-0">
            <Mail className="w-4 h-4 text-violet-600" />
          </div>
          <div>
            <p className="font-medium text-slate-800">{user.email}</p>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${TIER_STYLES[tier]}`}>
                {TIER_LABELS[tier]}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-100">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Calendar className="w-4 h-4 shrink-0" />
            <span>Member since {memberSince}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <BarChart3 className="w-4 h-4 shrink-0" />
            {chartsLoading
              ? <Loader2 className="w-3 h-3 animate-spin" />
              : <span>{charts.length} chart{charts.length !== 1 ? "s" : ""} created</span>
            }
          </div>
        </div>
      </div>

      {/* Subscription card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">Subscription</h2>

        {isFree ? (
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200">
              <Lock className="w-5 h-5 text-slate-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-slate-700">Free tier</p>
                <p className="text-sm text-slate-500 mt-0.5">
                  You can create charts and view your 12-palace grid. Unlock AI-generated readings and PDF export with a one-time upgrade.
                </p>
              </div>
            </div>

            <div className="border border-violet-200 bg-violet-50 rounded-xl p-5">
              <p className="font-semibold text-violet-800 mb-1">Unlock Full Access — $9.99</p>
              <ul className="text-sm text-violet-700 space-y-1 mb-4">
                <li>✦ AI-generated readings for all 4 report types</li>
                <li>✦ Core Personality, Relationships, Career & Current Period</li>
                <li>✦ PDF download of your complete report</li>
                <li>✦ All future charts you create</li>
              </ul>
              <button
                onClick={handleUpgrade}
                disabled={upgradeLoading}
                className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold px-6 py-2.5 rounded-xl transition-colors shadow-md shadow-violet-200"
              >
                {upgradeLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                {upgradeLoading ? "Redirecting to checkout…" : "Unlock full access"}
              </button>
              {upgradeError && (
                <p className="text-red-500 text-sm mt-2">{upgradeError}</p>
              )}
              <p className="text-xs text-violet-500 mt-2">One-time payment · Secure checkout via Stripe</p>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-3 p-4 bg-green-50 rounded-xl border border-green-200">
            <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-green-800">Full access unlocked</p>
              <p className="text-sm text-green-600 mt-0.5">
                You have access to all AI readings and PDF export for every chart you create.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
