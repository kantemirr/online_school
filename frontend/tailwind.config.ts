import type { Config } from 'tailwindcss'

// Дизайн-система CodeKids. Палитра: индиго (бренд) + бирюза + солнечный жёлтый +
// коралл, светлая тема. Токены продублированы в src/styles/tokens.css как CSS-переменные
// для рантайм-использования (sonner, конфетти).
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#EDEBFD',
          100: '#D7D1FA',
          200: '#B7ADF4',
          400: '#8A78EC',
          500: '#6C5CE7',
          DEFAULT: '#6C5CE7',
          600: '#5544D6',
          700: '#4536B8',
          900: '#2A2173',
        },
        teal: { 50: '#E1F7F6', 200: '#9BE4E0', 500: '#13C0BC', DEFAULT: '#13C0BC', 700: '#0C7F7B' },
        sun: { 50: '#FFF3D6', 200: '#FFE0A3', 500: '#FDB833', DEFAULT: '#FDB833', 700: '#B97D0A', ink: '#5A3E00' },
        coral: { 50: '#FFE3EE', 500: '#FF6B9D', DEFAULT: '#FF6B9D', 700: '#C23A6B' },
        success: { 50: '#E3F8EE', 500: '#34C77B', DEFAULT: '#34C77B', 700: '#137A4C' },
        danger: { 50: '#FDE9E9', 500: '#F26D6D', DEFAULT: '#F26D6D', 700: '#B23232' },
        warning: { 500: '#FBB13C', DEFAULT: '#FBB13C' },
        info: { 500: '#5B9DF9', DEFAULT: '#5B9DF9' },
        ink: '#20243A',
        muted: '#5A6072',
        hint: '#8A90A6',
        line: '#E7E9F2',
        cloud: '#F6F7FB',
        surface: '#FFFFFF',
      },
      fontFamily: {
        sans: ['Nunito', 'Segoe UI', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        xs: '0.75rem',
        sm: '0.875rem',
        base: '1rem',
        lg: '1.125rem',
        xl: '1.25rem',
        '2xl': '1.5rem',
        '3xl': '1.875rem',
        '4xl': '2.25rem',
      },
      borderRadius: { sm: '8px', md: '12px', lg: '16px', xl: '20px', '2xl': '28px' },
      boxShadow: {
        soft: '0 2px 8px rgba(108,92,231,0.06)',
        card: '0 6px 18px rgba(108,92,231,0.08)',
        pop: '0 12px 32px rgba(108,92,231,0.12)',
      },
      keyframes: {
        bob: { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-6px)' } },
        'pop-in': { '0%': { transform: 'scale(0.9)', opacity: '0' }, '100%': { transform: 'scale(1)', opacity: '1' } },
        shimmer: { '100%': { transform: 'translateX(100%)' } },
      },
      animation: {
        bob: 'bob 3s ease-in-out infinite',
        'pop-in': 'pop-in 0.25s ease-out',
        shimmer: 'shimmer 1.5s infinite',
      },
    },
  },
  plugins: [],
} satisfies Config
