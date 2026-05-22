"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { api } from "@/lib/api";

const TIMEZONES = [
  { label: "UTC-8  Pacific (PST)", value: -8 },
  { label: "UTC-7  Mountain (MST)", value: -7 },
  { label: "UTC-6  Central (CST)", value: -6 },
  { label: "UTC-5  Eastern (EST)", value: -5 },
  { label: "UTC+0  London (GMT)", value: 0 },
  { label: "UTC+8  Beijing/Taipei (CST)", value: 8 },
  { label: "UTC+9  Tokyo (JST)", value: 9 },
];

export default function NewChartPage() {
  const router = useRouter();
  const [date, setDate] = useState("");
  const [time, setTime] = useState("12:00");
  const [isMale, setIsMale] = useState<boolean>(true);
  const [tzOffset, setTzOffset] = useState(-5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!time) {
      setError("Birth time is required");
      return;
    }

    const today = new Date().toISOString().split("T")[0];
    if (date > today) {
      setError("Date of birth cannot be in the future");
      return;
    }

    setLoading(true);
    try {
      const chart = await api.charts.create({
        gregorian_date: date,
        birth_time: `${time}:00`,
        is_male: isMale,
        timezone_offset: tzOffset,
      });
      router.push(`/dashboard/charts/${chart.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create chart");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">New chart</h1>
      <p className="text-slate-500 text-sm mb-8">Enter birth details to calculate your Zi Wei Dou Shu chart.</p>

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-2xl p-6 space-y-5">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Date of birth
          </label>
          <input
            type="date"
            value={date}
            onChange={e => setDate(e.target.value)}
            required
            max={new Date().toISOString().split("T")[0]}
            className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-400"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Time of birth (local time)
          </label>
          <input
            type="time"
            value={time}
            onChange={e => setTime(e.target.value)}
            required
            className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-400"
          />
          <p className="text-xs text-slate-400 mt-1">If unknown, use 12:00 (noon)</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Gender</label>
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
                    : "border-slate-300 text-slate-600 hover:border-violet-300"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Timezone at birth
          </label>
          <select
            value={tzOffset}
            onChange={e => setTzOffset(Number(e.target.value))}
            className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-400"
          >
            {TIMEZONES.map(tz => (
              <option key={tz.value} value={tz.value}>{tz.label}</option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={loading || !date}
          className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          {loading ? "Calculating chart…" : "Generate chart"}
        </button>
      </form>
    </div>
  );
}
