/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Warm tinted neutrals — no pure black/white
        sand: {
          50: '#F9F6F1',
          100: '#F3EEE6',
          200: '#E8DFD2',
        },
        ink: {
          700: '#2A3B4D',
          800: '#1F2E3D',
          900: '#15212E',
        },
        petrol: {
          400: '#2B7A99',
          500: '#0E5C7A',
          600: '#0E4D6B',
          700: '#0A3A52',
        },
        turquoise: {
          400: '#2EC4B6',
          500: '#25A99B',
        },
        amber: {
          400: '#E8A23D',
          500: '#D98E2C',
        },
        rust: {
          500: '#D45D5D',
        },
        moss: {
          500: '#4A9B6E',
          600: '#3B8A5E',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans Arabic', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'xl2': '1rem',
      },
      maxWidth: {
        'mobile': '30rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },
    },
  },
  plugins: [],
}