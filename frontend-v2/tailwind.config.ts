import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // shadcn/ui defaults mapped to CSS variables
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },

        // Warm Neutrals — Light Theme Foundation
        "warm-bg": "#FAFAF8",
        "warm-surface": "#FFFFFF",
        "warm-border": "#E8E5DF",
        "warm-muted": "#F5F3EE",

        // Text hierarchy
        "text-main": "#1C1917",      // stone-900
        "text-secondary": "#78716C", // stone-500
        "text-muted": "#A8A29E",     // stone-400

        // Brand Accent — Amber
        brand: {
          50:  "#FFFBEB",
          100: "#FEF3C7",
          200: "#FDE68A",
          300: "#FCD34D",
          400: "#FBBF24",
          500: "#F59E0B",
          600: "#D97706",  // PRIMARY
          700: "#B45309",  // HOVER
          800: "#92400E",
          900: "#78350F",
        },

        // Semantic colors
        success: { DEFAULT: "#059669", light: "#D1FAE5", border: "#6EE7B7" },
        warning: { DEFAULT: "#D97706", light: "#FEF3C7", border: "#FCD34D" },
        error:   { DEFAULT: "#DC2626", light: "#FEE2E2", border: "#FCA5A5" },
        info:    { DEFAULT: "#2563EB", light: "#DBEAFE", border: "#93C5FD" },

        // Score metric colors (for the 8 metrics)
        score: {
          excellent: "#059669",  // 8-10
          good:      "#D97706",  // 6-7.9
          average:   "#EA580C",  // 4-5.9
          poor:      "#DC2626",  // 0-3.9
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
        serif: ["Instrument Serif", "Georgia", "serif"],
        mono:  ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        "display":  ["2.25rem", { lineHeight: "2.5rem",  fontWeight: "700" }],
        "heading":  ["1.5rem",  { lineHeight: "2rem",    fontWeight: "600" }],
        "subhead":  ["1.125rem",{ lineHeight: "1.75rem", fontWeight: "600" }],
        "body":     ["1rem",    { lineHeight: "1.625rem",fontWeight: "400" }],
        "small":    ["0.875rem",{ lineHeight: "1.25rem", fontWeight: "400" }],
        "micro":    ["0.75rem", { lineHeight: "1rem",    fontWeight: "400" }],
      },
      borderRadius: {
        "sm":  "0.25rem",
        "md":  "0.375rem",
        "lg":  "0.5rem",
        "xl":  "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
        "full":"9999px",
      },
      boxShadow: {
        "warm-sm": "0 1px 2px 0 rgba(28, 25, 23, 0.05)",
        "warm-md": "0 4px 6px -1px rgba(28, 25, 23, 0.08), 0 2px 4px -1px rgba(28, 25, 23, 0.04)",
        "warm-lg": "0 10px 15px -3px rgba(28, 25, 23, 0.08), 0 4px 6px -2px rgba(28, 25, 23, 0.03)",
        "warm-xl": "0 20px 25px -5px rgba(28, 25, 23, 0.08), 0 10px 10px -5px rgba(28, 25, 23, 0.02)",
        "brand":   "0 0 0 3px rgba(217, 119, 6, 0.12)",  // focus ring
      },
      spacing: {
        "4.5": "1.125rem",
        "13":  "3.25rem",
        "18":  "4.5rem",
        "72":  "18rem",
        "84":  "21rem",
        "88":  "22rem",
        "96":  "24rem",
        "128": "32rem",
      },
      animation: {
        "fade-in":     "fadeIn 0.3s ease-out",
        "slide-up":    "slideUp 0.35s ease-out",
        "pulse-brand": "pulseBrand 2s ease-in-out infinite",
        "spin-slow":   "spin 2s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%":   { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseBrand: {
          "0%, 100%": { opacity: "1" },
          "50%":      { opacity: "0.6" },
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
