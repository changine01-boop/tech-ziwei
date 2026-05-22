import Link from "next/link";
import { Star, Brain, BarChart3, ArrowRight, Sparkles } from "lucide-react";

const FEATURES = [
  {
    icon: Star,
    title: "Authentic Chart Calculation",
    body: "Precise Zi Wei Dou Shu charts derived from your birth date and time, following traditional calculation methods.",
  },
  {
    icon: Brain,
    title: "Psychological Reframing",
    body: "Ancient star archetypes translated into Jungian, attachment-theory, and growth-mindset language — no fatalism, no mysticism.",
  },
  {
    icon: BarChart3,
    title: "AI-Powered Narrative Reports",
    body: "Personalised readings in four areas: core personality, relationship patterns, career purpose, and current life period.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-violet-950 to-slate-950 text-white">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-6xl mx-auto">
        <span className="text-xl font-bold tracking-tight">
          ✦ Tech Zi Wei
        </span>
        <div className="flex gap-4">
          <Link href="/login" className="text-sm text-slate-300 hover:text-white transition-colors">
            Sign in
          </Link>
          <Link
            href="/register"
            className="text-sm bg-violet-600 hover:bg-violet-500 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Get started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="text-center px-6 py-24 max-w-4xl mx-auto">
        <div className="inline-block text-violet-300 text-sm font-medium tracking-widest uppercase mb-6 border border-violet-700 rounded-full px-4 py-1">
          Purple Star Astrology · Modern Psychology
        </div>
        <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6">
          Understand yourself through{" "}
          <span className="text-violet-400">ancient wisdom</span>
        </h1>
        <p className="text-xl text-slate-300 mb-10 max-w-2xl mx-auto leading-relaxed">
          Tech Zi Wei transforms Zi Wei Dou Shu — a 1,000-year-old Chinese
          astrology system — into the language of contemporary psychology.
          Discover your patterns, not your fate.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/register"
            className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors shadow-lg shadow-violet-900/50"
          >
            Get started <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            href="/try"
            className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/15 border border-white/20 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors backdrop-blur-sm"
          >
            <Sparkles className="w-5 h-5 text-violet-300" />
            Try it free
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto px-6 pb-24 grid md:grid-cols-3 gap-6">
        {FEATURES.map(({ icon: Icon, title, body }) => (
          <div
            key={title}
            className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm"
          >
            <div className="w-10 h-10 bg-violet-700/50 rounded-lg flex items-center justify-center mb-4">
              <Icon className="w-5 h-5 text-violet-300" />
            </div>
            <h3 className="font-semibold text-lg mb-2">{title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed">{body}</p>
          </div>
        ))}
      </section>

      {/* Sample palace grid teaser */}
      <section className="max-w-3xl mx-auto px-6 pb-32 text-center">
        <p className="text-slate-400 text-sm mb-6 uppercase tracking-widest">
          Your chart, visualised
        </p>
        <div className="grid grid-cols-4 grid-rows-4 gap-px bg-white/10 rounded-2xl overflow-hidden shadow-2xl shadow-violet-900/30 aspect-square max-w-sm mx-auto text-xs">
          {/* Decorative mini-grid preview */}
          {Array.from({ length: 12 }).map((_, i) => (
            <div
              key={i}
              className={`bg-slate-900 p-2 flex flex-col gap-1 ${
                i === 0 ? "border-2 border-violet-500" : ""
              }`}
            >
              <span className="text-violet-400 font-medium truncate">宮</span>
              <span className="text-slate-500">✦</span>
            </div>
          ))}
          <div className="col-span-2 row-span-2 bg-slate-800 flex items-center justify-center col-start-2 row-start-2">
            <span className="text-slate-500 text-lg">紫微</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 text-center py-8 text-slate-500 text-sm space-y-3">
        <div className="flex items-center justify-center gap-6">
          <Link href="/legal/privacy" className="hover:text-slate-300 transition-colors">Privacy Policy</Link>
          <Link href="/legal/terms" className="hover:text-slate-300 transition-colors">Terms of Service</Link>
          <Link href="/legal/disclaimer" className="hover:text-slate-300 transition-colors">Disclaimer</Link>
        </div>
        <p>© 2026 Tech Zi Wei. For self-reflection purposes only — not professional advice.</p>
      </footer>
    </div>
  );
}
