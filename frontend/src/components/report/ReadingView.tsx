"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { READING_TYPE_LABELS } from "@/lib/constants";
import type { ReadingResponse, ReadingType } from "@/lib/types";

interface Props {
  chartId: string;
  readingType: ReadingType;
}

const POLL_INTERVAL_MS = 3000;

export function ReadingView({ chartId, readingType }: Props) {
  const [reading, setReading] = useState<ReadingResponse | null>(null);
  const [error, setError] = useState("");
  const [requesting, setRequesting] = useState(false);

  const requestReading = useCallback(async () => {
    setRequesting(true);
    setError("");
    try {
      const r = await api.readings.request(chartId, readingType);
      setReading(r);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to request reading");
    } finally {
      setRequesting(false);
    }
  }, [chartId, readingType]);

  // Poll while status is pending/generating
  useEffect(() => {
    if (!reading) return;
    if (reading.status === "complete" || reading.status === "failed") return;

    const id = setInterval(async () => {
      try {
        const refreshed = await api.readings.request(chartId, readingType);
        setReading(refreshed);
      } catch {
        // ignore poll errors
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(id);
  }, [reading, chartId, readingType]);

  if (!reading) {
    return (
      <div className="text-center py-10">
        <p className="text-slate-500 mb-4 text-sm">
          Generate your {READING_TYPE_LABELS[readingType]} reading
        </p>
        <button
          onClick={requestReading}
          disabled={requesting}
          className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white px-5 py-2.5 rounded-lg font-medium transition-colors"
        >
          {requesting && <Loader2 className="w-4 h-4 animate-spin" />}
          Generate reading
        </button>
        {error && <p className="text-red-400 text-sm mt-3">{error}</p>}
      </div>
    );
  }

  if (reading.status === "pending" || reading.status === "generating") {
    return (
      <div className="flex flex-col items-center gap-3 py-12 text-slate-500">
        <Loader2 className="w-6 h-6 animate-spin text-violet-500" />
        <p className="text-sm">Generating your reading… this usually takes 15–30 seconds.</p>
      </div>
    );
  }

  if (reading.status === "failed") {
    return (
      <div className="text-center py-10">
        <p className="text-red-400 mb-4 text-sm">Generation failed. Please try again.</p>
        <button
          onClick={requestReading}
          className="inline-flex items-center gap-2 text-slate-500 hover:text-slate-700 text-sm"
        >
          <RefreshCw className="w-4 h-4" /> Retry
        </button>
      </div>
    );
  }

  return (
    <div className="prose prose-slate max-w-none">
      <div className="whitespace-pre-wrap text-slate-700 leading-relaxed text-sm">
        {reading.content}
      </div>
      {reading.completed_at && (
        <p className="text-xs text-slate-400 mt-6">
          Generated {new Date(reading.completed_at).toLocaleString()}
        </p>
      )}
    </div>
  );
}
