/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        itaca: {
          blue: "#1393B2",
          bg: "#181A1B",
          panel: "#25282A",
          gold: "#998000",
          red: "#B50F19",
          text: "#F5F5F5",
          subtext: "#E8E8E8",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 10px 30px rgba(0, 0, 0, 0.35)",
      },
    },
  },
  plugins: [],
};
