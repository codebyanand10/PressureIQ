/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0E1117',
        card: '#161B22',
        'card-hover': '#1F242C',
        border: '#30363D',
        'border-light': '#3D444D',
        primary: {
          DEFAULT: '#00FFCC',
          dark: '#00CC99',
          light: '#33FFD6',
        },
        secondary: '#38BDF8',
        accent: '#818CF8',
        gold: '#F59E0B',
        emerald: '#10B981',
        danger: '#EF4444',
        text: {
          main: '#F0F6FC',
          muted: '#8B949E',
          dim: '#484F58'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      }
    },
  },
  plugins: [],
}
