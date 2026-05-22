import Link from "next/link";

export default function LegalLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <nav className="border-b border-slate-200 bg-white">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-lg font-bold tracking-tight text-slate-900">
            ✦ Tech Zi Wei
          </Link>
          <Link href="/" className="text-sm text-slate-500 hover:text-slate-800 transition-colors">
            ← Back to home
          </Link>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-6 py-12">
        {children}
      </main>

      <footer className="border-t border-slate-200 mt-16 py-8 text-center text-slate-400 text-sm">
        <div className="flex items-center justify-center gap-6 mb-2">
          <Link href="/legal/privacy" className="hover:text-slate-600 transition-colors">Privacy Policy</Link>
          <Link href="/legal/terms" className="hover:text-slate-600 transition-colors">Terms of Service</Link>
          <Link href="/legal/disclaimer" className="hover:text-slate-600 transition-colors">Disclaimer</Link>
        </div>
        <p>© {new Date().getFullYear()} Tech Zi Wei. All rights reserved.</p>
      </footer>
    </div>
  );
}
