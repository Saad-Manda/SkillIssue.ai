import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers/Providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SkillIssue.ai — AI-Powered Mock Interviews",
  description:
    "Get context-aware, AI-driven mock interviews tailored to your profile and target job description. Understand exactly where you stand before the real interview.",
  keywords: ["mock interview", "AI interview prep", "job interview practice"],
  openGraph: {
    title: "SkillIssue.ai",
    description: "AI-Powered Mock Interviewer Platform",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
