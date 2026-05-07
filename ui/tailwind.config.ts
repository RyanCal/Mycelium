import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#17211b',
        moss: '#37543d',
        fern: '#7aa66a',
        clay: '#b86f52',
        mist: '#eef2ee',
      },
    },
  },
  plugins: [],
};

export default config;
