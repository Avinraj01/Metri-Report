/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        editorial: ['"Space Grotesk"', '"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        metri: {
          navy: '#0b1120',
          dark: '#080d1a',
          surface: '#0f172a',
          card: '#131d31',
          border: '#1e293b',
          blue: '#2563eb',
          cobalt: '#1d4ed8',
          accent: '#38bdf8',
          teal: '#0d9488',
          pass: '#10b981',
          fail: '#f43f5e',
          warn: '#f59e0b',
          muted: '#94a3b8',
          ivory: '#f8fafc',
          amber: '#d97706'
        }
      }
    },
  },
  plugins: [],
}
