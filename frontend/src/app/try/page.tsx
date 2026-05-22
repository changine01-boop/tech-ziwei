"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight, Loader2, Sparkles, Star } from "lucide-react";
import { api } from "@/lib/api";
import { BRANCHES, STEMS, WU_XING_JU_LABELS, ZIWEI_GROUP, TIANFU_GROUP } from "@/lib/constants";
import type { PreviewResponse } from "@/lib/types";

const TIMEZONES = [
  { label: "UTC-8  Pacific (PST)", value: -8 },
  { label: "UTC-7  Mountain (MST)", value: -7 },
  { label: "UTC-6  Central (CST)", value: -6 },
  { label: "UTC-5  Eastern (EST)", value: -5 },
  { label: "UTC+0  London (GMT)", value: 0 },
  { label: "UTC+8  Beijing / Taipei (CST)", value: 8 },
  { label: "UTC+9  Tokyo (JST)", value: 9 },
];

const STAR_ARCHETYPES: Record<string, string> = {
  "紫微": "Authority Archetype",
  "天機": "Strategic Mind",
  "太陽": "Solar Drive",
  "武曲": "Boundary-Setter",
  "天同": "Harmony-Seeker",
  "廉貞": "Integrity Fire",
  "天府": "Secure Base",
  "太陰": "Lunar Depth",
  "貪狼": "Appetite for Experience",
  "巨門": "Verbal Intelligence",
  "天相": "Collaborative Diplomat",
  "天梁": "Elder Wisdom",
  "七殺": "Transformative Edge",
  "破軍": "Pioneer Spirit",
};

function StarPill({ name }: { name: string }) {
  const isZiwei = ZIWEI_GROUP.has(name);
  const isTianfu = TIANFU_GROUP.has(name);
  const archetype = STAR_ARCHETYPES[name];

  return (
    <div
      className={`inline-flex flex-col items-center gap-0.5 px-3 py-2 rounded-xl border text-center ${
        isZiwei
          ? "bg-violet-900/40 border-violet-500/50 text-violet-200"
          : isTianfu
          ? "bg-amber-900/30 border-amber-500/40 text-amber-200"
          : "bg-slate-800/60 border-slate-600/40 text-slate-300"
      }`}
    >
      <span className="text-sm font-semibold">{name}</span>
      {archetype && (
        <span className="text-xs opacity-70">{archetype}</span>
      )}
    </div>
  );
}

function PreviewResult({ result }: { result: PreviewResponse }) {
  const stemLabel = STEMS[result.ming_branch % 10] ?? "";
  const branchLabel = BRANCHES[result.ming_branch] ?? "";

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header badge */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 bg-violet-700/30 border border-violet-500/40 rounded-full px-4 py-1.5 text-violet-300 text-sm mb-4">
          <Star className="w-3.5 h-3.5" />
          Your Chart Preview
        </div>
        <h2 className="text-2xl font-bold text-white">
          {result.year_ganzhi} Year · {result.wu_xing_ju_label}
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          Life Palace (命宮): {result.ming_ganzhi} · {result.ming_palace_name}
        </p>
      </div>

      {/* Main stars */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
        <p className="text-xs text-slate-400 uppercase tracking-widest mb-3">
          Stars in Your Life Palace
        </p>
        {result.main_stars.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {result.main_stars.map(star => (
              <StarPill key={star} name={star} />
            ))}
          </div>
        ) : (
          <p className="text-slate-500 text-sm italic">
            No major stars reside in your Life Palace — neighbouring palaces exert strong influence.
          </p>
        )}
      </div>

      {/* Hook / teaser */}
      <div className="relative bg-gradient-to-br from-violet-900/50 to-slate-900/80 border border-violet-500/30 rounded-2xl p-6">
        <div className="absolute top-4 right-4 opacity-20">
          <Sparkles className="w-8 h-8 text-violet-300" />
        </div>
        <p className="text-slate-200 leading-relaxed text-sm">
          {result.hook}
        </p>
      </div>

      {/* What's in the full reading */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
        <p className="text-xs text-slate-400 uppercase tracking-widest mb-3">
          Full reading includes
        </p>
        <ul className="space-y-2">
          {[
            "Core Personality — all 12 palaces analysed",
            "Relationship Patterns — attachment style & romantic tendencies",
            "Career & Purpose — calling, finances, inner motivation",
            "Current Period — your active 大限 decade & what it's asking of you",
            "PDF download of your complete report",
          ].map(item => (
            <li key={item} className="flex items-start gap-2 text-sm text-slate-300">
              <span className="text-violet-400 mt-0.5">✦</span>
              {item}
            </li>
          ))}
        </ul>
      </div>

      {/* CTA */}
      <div className="text-center space-y-3 pt-2">
        <Link
          href="/register"
          className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors shadow-lg shadow-violet-900/50"
        >
          Get your full reading <ArrowRight className="w-5 h-5" />
        </Link>
        <p className="text-xs text-slate-500">
          Free to register · Full report unlocked for $9.99 one-time
        </p>
      </div>
    </div>
  );
}

export default function TryPage() {
  const [date, setDate] = useState("");
  const [birthTime, setBirthTime] = useState("12:00");
  const [isMale, setIsMale] = useState<boolean>(true);
  const [tzOffset, setTzOffset] = useState(-5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<PreviewResponse | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api.preview.calculate({
        gregorian_date: date,
        birth_time: `${birthTime}:00`,
        is_male: isMale,
        timezone_offset: tzOffset,
      });
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Calculation failed. Please check your input.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-violet-950 to-slate-950 text-white">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-3xl mx-auto">
        <Link href="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-white text-sm transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back
        </Link>
        <span className="text-lg font-bold tracking-tight text-white">✦ Tech Zi Wei</span>
        <Link
          href="/register"
          className="text-sm bg-violet-600 hover:bg-violet-500 px-4 py-2 rounded-lg font-medium transition-colors"
        >
          Get started
        </Link>
      </nav>

      <div className="max-w-lg mx-auto px-6 pt-8 pb-24">
        {/* Page heading */}
        <div className="text-center mb-10">
          <div className="inline-block text-violet-300 text-sm font-medium tracking-widest uppercase mb-4 border border-violet-700 rounded-full px-4 py-1">
            Free Preview
          </div>
          <h1 className="text-3xl font-bold leading-tight mb-3">
            See your Life Palace
          </h1>
          <p className="text-slate-400 text-sm leading-relaxed">
            Enter your birth details to instantly reveal your 命宮 (Life Palace) —
            the foundation of your Zi Wei Dou Shu chart and your core psychological archetype.
          </p>
        </div>

        {!result ? (
          <form
            onSubmit={handleSubmit}
            className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-5 backdrop-blur-sm"
          >
            {error && (
              <div className="bg-red-900/40 border border-red-500/40 text-red-300 text-sm rounded-lg px-4 py-3">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Date of birth
              </label>
              <input
                type="date"
                value={date}
                onChange={e => setDate(e.target.value)}
                required
                max={new Date().toISOString().split("T")[0]}
                className="w-full bg-slate-900/70 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Time of birth (local time)
              </label>
              <input
                type="time"
                value={birthTime}
                onChange={e => setBirthTime(e.target.value)}
                required
                className="w-full bg-slate-900/70 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              />
              <p className="text-xs text-slate-500 mt-1">If unknown, use 12:00 (noon) — the chart will still be meaningful</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Gender</label>
              <div className="flex gap-3">
                {[
                  { label: "Male", value: true },
                  { label: "Female", value: false },
                ].map(opt => (
                  <button
                    key={opt.label}
                    type="button"
                    onClick={() => setIsMale(opt.value)}
                    className={`flex-1 py-2.5 rounded-lg border text-sm font-medium transition-colors ${
                      isMale === opt.value
                        ? "bg-violet-600 border-violet-600 text-white"
                        : "border-slate-600 text-slate-400 hover:border-violet-400 hover:text-slate-200"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Timezone at birth
              </label>
              <select
                value={tzOffset}
                onChange={e => setTzOffset(Number(e.target.value))}
                className="w-full bg-slate-900/70 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              >
                {TIMEZONES.map(tz => (
                  <option key={tz.value} value={tz.value}>{tz.label}</option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              disabled={loading || !date}
              className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold py-3.5 rounded-xl transition-colors flex items-center justify-center gap-2 mt-2"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {loading ? "Calculating your chart…" : "Reveal my Life Palace"}
            </button>
          </form>
        ) : (
          <div>
            <PreviewResult result={result} />
            <button
              onClick={() => setResult(null)}
              className="mt-6 w-full text-slate-500 hover:text-slate-300 text-sm transition-colors py-2"
            >
              ← Try different birth details
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
