import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#CC3366",
          50: "#FBEAF1",
          100: "#F5CBDD",
          200: "#EB9EBE",
          300: "#E0709F",
          400: "#D65181",
          500: "#CC3366",
          600: "#A82951",
          700: "#821F3E",
          800: "#5C162C",
          900: "#380D1B",
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
        sans: [
          "Heebo",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Arial",
          "sans-serif",
        ],
      },
      borderRadius: {
        card: "0.75rem",
      },
    },
  },
  plugins: [],
};

export default config;
