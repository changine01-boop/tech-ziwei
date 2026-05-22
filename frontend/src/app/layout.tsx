import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata: Metadata = {
  title: "Tech Zi Wei — Psychological Astrology",
  description:
    "Discover your psychological blueprint through the ancient wisdom of Zi Wei Dou Shu, translated into modern Western psychology.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
