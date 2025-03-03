// tailwind.config.js
module.exports = {
    content: [
      "./src/**/*.{js,jsx,ts,tsx}",
      "./public/index.html",
    ],
    theme: {
      extend: {
        colors: {
          primary: {
            light: '#4da6ff',
            DEFAULT: '#0077cc',
            dark: '#004c8c',
          },
          secondary: {
            light: '#8c9eff',
            DEFAULT: '#536dfe',
            dark: '#3d5afe',
          },
        },
        fontFamily: {
          sans: ['Inter', 'sans-serif'],
        },
      },
    },
    plugins: [],
  }