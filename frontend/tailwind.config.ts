import type { Config } from 'tailwindcss';

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ivory: '#F4F1EA',
        charcoal: '#232323',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Source Serif 4', 'serif'],
      },
      spacing: {
        '1': '0.25rem', // 4px
        '2': '0.5rem',  // 8px
        '3': '0.75rem', // 12px
        '4': '1rem',    // 16px
        '5': '1.25rem', // 20px
        '6': '1.5rem',  // 24px
        '8': '2rem',    // 32px
        '10': '2.5rem', // 40px
        '12': '3rem',   // 48px
        '16': '4rem',   // 64px
      },
      borderRadius: {
        'sm': '4px',
        DEFAULT: '6px',
        'md': '8px',
        'lg': '12px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(35, 35, 35, 0.05)',
        DEFAULT: '0 1px 3px 0 rgba(35, 35, 35, 0.1), 0 1px 2px -1px rgba(35, 35, 35, 0.1)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
} satisfies Config;
