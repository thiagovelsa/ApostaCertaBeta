import defaultTheme from 'tailwindcss/defaultTheme';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    ...defaultTheme,
    extend: {
      colors: {
        // Primary Color - Lime Green
        primary: {
          50: '#f7fee7',
          100: '#ecfccf',
          200: '#d9f99d',
          300: '#bfef45',
          400: '#a3e635',
          500: '#84cc16', // Main primary
          600: '#65a30d',
          700: '#4d7c0f',
          800: '#3f6212',
          900: '#365314',
        },
        // Dark Background Layers
        dark: {
          primary: '#0a0a0a',
          secondary: '#171717',
          tertiary: '#262626',
          quaternary: '#404040',
        },
        // Semantic Colors
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#3b82f6',
        // CV Classification Colors
        cv: {
          muitoEstavel: '#22c55e',
          estavel: '#84cc16',
          moderado: '#eab308',
          instavel: '#f97316',
          muitoInstavel: '#ef4444',
        },
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['Space Mono', 'monospace'],
      },
      boxShadow: {
        'glow': '0 0 20px rgba(132, 204, 22, 0.3)',
        'glow-strong': '0 0 30px rgba(132, 204, 22, 0.5)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-up': 'scaleUp 0.2s ease-out',
        'pulse-glow': 'pulseGlow 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleUp: {
          '0%': { transform: 'scale(0.95)' },
          '100%': { transform: 'scale(1)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(132, 204, 22, 0.3)' },
          '50%': { boxShadow: '0 0 30px rgba(132, 204, 22, 0.5)' },
        },
      },
    },
  },
  plugins: [],
}
