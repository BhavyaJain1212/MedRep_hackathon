/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', "system-ui", "-apple-system", "sans-serif"],
      },
      colors: {
        navy: {
          950: "#0a0f1e",
          900: "#0f172a",
          800: "#162036",
          700: "#1e2d4a",
          600: "#2a3f5f",
        },
      },
    },
  },
  plugins: [],
};

