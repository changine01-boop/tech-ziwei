import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <nav className="px-6 py-4">
        <Link href="/" className="text-white font-bold text-lg">✦ Tech Zi Wei</Link>
      </nav>
      <div className="flex-1 flex items-center justify-center px-4">
        {children}
      </div>
    </div>
  );
}
