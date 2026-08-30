import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#3F8420",
          50: "#EEF7E6",
          100: "#D6EDC3",
          200: "#B4DF93",
          300: "#8ECB5E",
          400: "#63AE33",
          500: "#3F8420",
          600: "#336B19",
          700: "#285214",
          800: "#1D3B0E",
          900: "#132709",
        },
        accent: {
          DEFAULT: "#85C441",
          50: "#F1F9E7",
          100: "#DEF0C4",
          200: "#C2E399",
          300: "#A6D66E",
          400: "#85C441",
          500: "#6BA730",
          600: "#528024",
          700: "#3B5C1A",
        },
        ink: {
          DEFAULT: "#333333",
          muted: "#5C5C5C",
        },
        rating: {
          green: "#85C441",
          yellow: "#E6B800",
          red: "#D64545",
        },
      },
      fontFamily: {
        sans: ["Heebo", "system-ui", "-apple-system", "Segoe UI", "Arial", "sans-serif"],
      },
      borderRadius: {
        card: "0.75rem",
      },
    },
  },
  plugins: [],
};

export default config;
