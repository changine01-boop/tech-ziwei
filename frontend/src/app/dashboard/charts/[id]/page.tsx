"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { BRANCHES, STEMS, WU_XING_JU_LABELS, READING_TYPE_LABELS } from "@/lib/constants";
import { PalaceGrid } from "@/components/chart/PalaceGrid";
import { ReadingView } from "@/components/report/ReadingView";
import type { ChartResponse, ReadingType } from "@/lib/types";

const TABS: { key: ReadingType; label: string }[] = [
  { key: "core",         label: READING_TYPE_LABELS.core },
  { key: "relationship", label: READING_TYPE_LABELS.relationship },
  { key: "career",       label: READING_TYPE_LABELS.career },
  { key: "annual",       label: READING_TYPE_LABELS.annual },
];

export default function ChartDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [chart, setChart] = useState<ChartResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<ReadingType>("core");

  useEffect(() => {
    api.charts.get(id)
      .then(setChart)
      .catch(() => router.push("/dashboard"))
      .finally(() => setLoading(false));
  }, [id, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-40">
        <Loader2 className="w-5 h-5 animate-spin text-violet-500" />
      </div>
    );
  }

  if (!chart) return null;

  const yearGanzhi = `${STEMS[chart.year_stem]}${BRANCHES[chart.year_branch]}`;
  const ju = WU_XING_JU_LABELS[chart.wu_xing_ju] ?? "";

  return (
    <div className="max-w-5xl">
      {/* Back + title */}
      <div className="mb-6">
        <Link href="/dashboard" className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-600 mb-4">
          <ArrowLeft className="w-4 h-4" /> Back to charts
        </Link>
        <div className="flex items-baseline gap-3">
          <h1 className="text-2xl font-bold text-slate-900">
            {yearGanzhi} 年 · {ju}
          </h1>
          <span className={`text-xs px-2 py-0.5 rounded-full ${chart.is_male ? "bg-blue-50 text-blue-600" : "bg-pink-50 text-pink-600"}`}>
            {chart.is_male ? "Male" : "Female"}
          </span>
        </div>
        <p className="text-slate-400 text-sm mt-1">
          {chart.gregorian_date} · 農曆 {chart.lunar_year}/{chart.lunar_month}/{chart.lunar_day}
          {chart.is_leap_month ? " 閏" : ""}
        </p>
      </div>

      {/* Palace grid */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 mb-6 shadow-sm">
        <PalaceGrid chart={chart} />
      </div>

      {/* Major periods summary */}
      {chart.major_periods.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 mb-6 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-600 mb-3 uppercase tracking-wide">
            Major Periods (大限)
          </h2>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {chart.major_periods.slice(0, 10).map(p => (
              <div
                key={p.index}
                className="shrink-0 border border-slate-200 rounded-lg px-3 py-2 text-center min-w-[80px]"
              >
                <div className="text-xs text-slate-400">{p.start_age}–{p.end_age}</div>
                <div className="text-xs font-medium text-slate-700 mt-0.5">{p.palace_name}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Readings */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        {/* Tab bar */}
        <div className="flex border-b border-slate-200">
          {TABS.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? "text-violet-600 border-b-2 border-violet-600 bg-violet-50/50"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Reading content */}
        <div className="p-6">
          <ReadingView chartId={chart.id} readingType={activeTab} />
        </div>
      </div>
    </div>
  );
}
