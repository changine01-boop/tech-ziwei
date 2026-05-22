"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Calendar, User, ChevronRight, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { BRANCHES, STEMS, WU_XING_JU_LABELS } from "@/lib/constants";
import type { ChartResponse } from "@/lib/types";

export default function DashboardPage() {
  const [charts, setCharts] = useState<ChartResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.charts.list()
      .then(setCharts)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-40">
        <Loader2 className="w-5 h-5 animate-spin text-violet-500" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">My Charts</h1>
          <p className="text-slate-500 text-sm mt-1">
            {charts.length} chart{charts.length !== 1 ? "s" : ""} saved
          </p>
        </div>
        <Link
          href="/dashboard/new"
          className="flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" /> New chart
        </Link>
      </div>

      {charts.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-slate-200">
          <div className="text-4xl mb-4">✦</div>
          <h2 className="text-lg font-semibold text-slate-700 mb-2">No charts yet</h2>
          <p className="text-slate-400 text-sm mb-6">
            Create your first chart to discover your psychological blueprint.
          </p>
          <Link
            href="/dashboard/new"
            className="inline-flex items-center gap-2 bg-violet-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium"
          >
            <Plus className="w-4 h-4" /> Generate chart
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {charts.map(chart => {
            const yearGanzhi = `${STEMS[chart.year_stem]}${BRANCHES[chart.year_branch]}`;
            const ju = WU_XING_JU_LABELS[chart.wu_xing_ju] ?? "";
            return (
              <Link
                key={chart.id}
                href={`/dashboard/charts/${chart.id}`}
                className="flex items-center justify-between bg-white border border-slate-200 rounded-xl px-5 py-4 hover:border-violet-300 hover:shadow-sm transition-all group"
              >
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-slate-800">
                      {yearGanzhi} 年 · {ju}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${chart.is_male ? "bg-blue-50 text-blue-600" : "bg-pink-50 text-pink-600"}`}>
                      {chart.is_male ? "Male" : "Female"}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" /> {chart.gregorian_date}
                    </span>
                    <span>農曆 {chart.lunar_year}/{chart.lunar_month}/{chart.lunar_day}</span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-violet-400 transition-colors" />
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
