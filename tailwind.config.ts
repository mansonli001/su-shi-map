import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // 「行吟山河」配色（设计稿对齐）
        ink: {
          DEFAULT: '#1A1008',
          mid: '#3D2B1F',
          lt:  '#5F5E5A',
          // 兼容旧 ink-50/100/.../900（防止历史样式崩）
          50:  '#FAF6F0',
          100: '#F0E9DF',
          200: '#D4C28F',
          300: '#BFAD7A',
          400: '#AB9765',
          500: '#BA7517',  // 中金（旧赭金锚点）
          600: '#3D2B1F',
          700: '#2A2008',
          800: '#1A1008',
          900: '#0F0905',
        },
        gold: {
          DEFAULT: '#FAC775',
          m: '#BA7517',
          d: '#EF9F27',
          light: '#FAEEDA',
        },
        paper: {
          DEFAULT: '#FAF6F0',
          2: '#F0E9DF',
          base: '#F1EFE8',
        },
        // 4 类阶段色
        birth: { DEFAULT: '#085041', light: '#5DCAA5' },
        office: { DEFAULT: '#0C447C', light: '#85B7EB' },
        exile: { DEFAULT: '#712B13', light: '#F0997B' },
        tour: { DEFAULT: '#633806', light: '#C9975A' },
        // 兼容旧名
        inkBlack: '#1A1008',
      },
      fontFamily: {
        serif: ['LXGW WenKai', 'Songti SC', 'STSong', 'SimSun', 'serif'],
        sans:  ['LXGW WenKai', 'PingFang SC', 'Microsoft YaHei', 'system-ui', 'sans-serif'],
        wenkai: ['LXGW WenKai', 'serif'],
      },
      letterSpacing: {
        wider2: '0.16em',
        widest2: '0.25em',
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
