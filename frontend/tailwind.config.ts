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
          DEFAULT: "#2A2E26",
          muted: "#5E655A",
          soft: "#858C7E",
        },
        rating: {
          green: "#6FB03A",
          yellow: "#E0A82E",
          red: "#D64545",
        },
        surface: {
          DEFAULT: "#F3F6EC",
          sunken: "#EAEEE0",
          raised: "#FFFFFF",
        },
        slate: {
          50: "#F7F9F2",
          100: "#EEF1E7",
          200: "#E1E5D7",
          300: "#CBD1BE",
          400: "#9AA18C",
          500: "#767D69",
          600: "#616854",
          700: "#4C5241",
          800: "#363B2E",
          900: "#262A20",
          950: "#171A12",
        },
      },
      fontFamily: {
        sans: ["Heebo", "system-ui", "-apple-system", "Segoe UI", "Arial", "sans-serif"],
      },
      fontSize: {
        eyebrow: ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.14em", fontWeight: "700" }],
        display: ["2rem", { lineHeight: "1.15", letterSpacing: "-0.015em", fontWeight: "300" }],
      },
      borderRadius: {
        card: "1rem",
        control: "0.75rem",
      },
      boxShadow: {
        soft: "0 1px 2px -1px rgba(38, 52, 20, 0.10), 0 2px 6px -2px rgba(38, 52, 20, 0.06)",
        card: "0 1px 3px -1px rgba(38, 52, 20, 0.08), 0 6px 16px -8px rgba(38, 52, 20, 0.10)",
        lift: "0 2px 6px -2px rgba(38, 52, 20, 0.12), 0 14px 30px -12px rgba(38, 52, 20, 0.16)",
        brand: "0 2px 6px -1px rgba(63, 132, 32, 0.28), 0 10px 22px -8px rgba(63, 132, 32, 0.32)",
        "brand-sm": "0 1px 2px rgba(63, 132, 32, 0.20), 0 4px 10px -4px rgba(63, 132, 32, 0.28)",
        ring: "0 0 0 1px rgba(63, 132, 32, 0.12)",
      },
      backgroundImage: {
        brand: "linear-gradient(135deg, #4B9426 0%, #3F8420 55%, #336B19 100%)",
        "brand-soft": "linear-gradient(135deg, #EEF7E6 0%, #E1F1D0 100%)",
        canvas: "radial-gradient(120% 90% at 100% 0%, #F6F9F0 0%, #F3F6EC 42%, #EEF2E4 100%)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.4s cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
