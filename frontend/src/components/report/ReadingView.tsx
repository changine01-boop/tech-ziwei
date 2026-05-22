"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2, Lock, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { NetworkError, getErrorMessage } from "@/lib/errors";
import { READING_TYPE_LABELS } from "@/lib/constants";
import type { ReadingResponse, ReadingType } from "@/lib/types";

interface Props {
  chartId: string;
  readingType: ReadingType;
  isPaid: boolean;
}

const POLL_INTERVAL_MS = 3000;

function PaywallBanner() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isNetworkError, setIsNetworkError] = useState(false);

  async function handleUnlock() {
    setLoading(true);
    setError("");
    setIsNetworkError(false);
    try {
      const { url } = await api.payments.createCheckoutSession();
      window.location.href = url;
    } catch (e: unknown) {
      const isNetwork = e instanceof NetworkError;
      setIsNetworkError(isNetwork);
      setError(getErrorMessage(e));
      setLoading(false);
    }
  }

  return (
    <div className="text-center py-12 px-6">
      <div className="w-14 h-14 bg-violet-100 rounded-full flex items-center justify-center mx-auto mb-5">
        <Lock className="w-6 h-6 text-violet-500" />
      </div>
      <h3 className="text-lg font-semibold text-slate-800 mb-2">
        Unlock your full reading
      </h3>
      <p className="text-slate-500 text-sm mb-6 max-w-sm mx-auto">
        Get AI-generated psychological insights for all four areas — personality,
        relationships, career, and annual themes — for every chart you create.
      </p>
      <button
        onClick={handleUnlock}
        disabled={loading}
        className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold px-6 py-3 rounded-xl transition-colors shadow-md shadow-violet-200"
      >
        {loading && <Loader2 className="w-4 h-4 animate-spin" />}
        {loading ? "Redirecting…" : "Unlock full report — $9.99"}
      </button>
      <p className="text-xs text-slate-400 mt-3">One-time payment · Secure checkout via Stripe</p>
      {error && (
        <p className={`text-sm mt-3 ${isNetworkError ? "text-slate-500" : "text-red-400"}`}>
          {error}
        </p>
      )}
    </div>
  );
}

export function ReadingView({ chartId, readingType, isPaid }: Props) {
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

  useEffect(() => {
    if (!reading) return;
    if (reading.status === "complete" || reading.status === "failed") return;

    const id = setInterval(async () => {
      try {
        const refreshed = await api.readings.get(chartId, readingType);
        setReading(refreshed);
      } catch {
        // ignore poll errors
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(id);
  }, [reading, chartId, readingType]);

  if (!isPaid) {
    return <PaywallBanner />;
  }

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
