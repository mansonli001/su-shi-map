import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // 水墨配色
        ink: {
          50:  '#F5E6C8',  // 宣纸色（背景）
          100: '#E8D5A3',
          200: '#D4C28F',
          300: '#BFAD7A',
          400: '#AB9765',
          500: '#8B6914',  // 赭金（主题色）
          600: '#6B5010',
          700: '#4A380C',
          800: '#2A2008',
          900: '#1A1405',
        },
        paper: '#F5E6C8',
        inkBlack: '#1A1405',
      },
      fontFamily: {
        serif: ['Noto Serif SC', 'SimSun', 'STSong', 'serif'],
        sans: ['Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
} satisfies Config;

export default config;
