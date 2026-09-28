/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        priva: {
          bg: "#0B0F19",
          card: "#111827",
          cardHover: "#1F2937",
          border: "#1E293B",
          borderLight: "#334155",
          primary: "#3B82F6",
          primaryHover: "#2563EB",
          accent: "#60A5FA",
          text: "#F8FAFC",
          muted: "#94A3B8",
          low: "#10B981",       // Green
          medium: "#F59E0B",    // Amber
          high: "#F97316",      // Orange
          critical: "#EF4444",  // Red
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Courier New", "monospace"],
      }
    },
  },
  plugins: [],
}
