/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#14213D",
          50: "#EEF1F6",
          100: "#D7DEE9",
          400: "#4B5C82",
          700: "#1C2B4D",
          900: "#0F1830",
        },
        brand: {
          DEFAULT: "#2F6F5E",
          50: "#EAF3F0",
          100: "#CFE5DD",
          300: "#7FB3A3",
          500: "#2F6F5E",
          600: "#256156",
          700: "#1B4940",
          900: "#0E2C26",
        },
        amber: {
          DEFAULT: "#E8A33D",
          100: "#FBE8C9",
          500: "#E8A33D",
          600: "#C9852A",
        },
        critical: {
          DEFAULT: "#DC2626",
          100: "#FBDADA",
          500: "#DC2626",
        },
        surface: {
          light: "#F7F8F6",
          card: "#FFFFFF",
          dark: "#0F1B1A",
          darkcard: "#16241F",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 27, 26, 0.06), 0 1px 12px rgba(15, 27, 26, 0.04)",
        popover: "0 8px 24px rgba(15, 27, 26, 0.16)",
      },
      borderRadius: {
        xl: "0.875rem",
      },
      keyframes: {
        "fade-in": { from: { opacity: 0 }, to: { opacity: 1 } },
        "slide-up": { from: { opacity: 0, transform: "translateY(8px)" }, to: { opacity: 1, transform: "translateY(0)" } },
      },
      animation: {
        "fade-in": "fade-in 0.15s ease-out",
        "slide-up": "slide-up 0.2s ease-out",
      },
    },
  },
  plugins: [],
};
