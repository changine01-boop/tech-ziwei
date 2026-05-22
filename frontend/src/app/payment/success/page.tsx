"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { CheckCircle2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function PaymentSuccessPage() {
  const { refetchUser } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Refresh user data so subscription_tier updates without a full reload
    refetchUser().catch(() => null);
  }, [refetchUser]);

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-10 max-w-md w-full text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-5">
          <CheckCircle2 className="w-8 h-8 text-green-500" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Payment successful!</h1>
        <p className="text-slate-500 mb-8">
          Your full report access is now unlocked. All four reading types are available
          for every chart you create.
        </p>
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
          onClick={() => router.push("/dashboard")}
        >
          Go to my charts
        </Link>
      </div>
    </div>
  );
}
