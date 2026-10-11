/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: "#131316",
        "surface-dim": "#131316",
        "surface-bright": "#39393c",
        "surface-container-lowest": "#0e0e11",
        "surface-container-low": "#1b1b1e",
        "surface-container": "#1f1f22",
        "surface-container-high": "#2a2a2d",
        "surface-container-highest": "#353438",
        "on-surface": "#e4e1e6",
        "on-surface-variant": "#d8c3ad",
        outline: "#a08e7a",
        "outline-variant": "#534434",
        primary: "#ffc174",
        "primary-container": "#f59e0b",
        "on-primary-container": "#613b00",
        secondary: "#4edea3",
        "secondary-container": "#00a572",
        tertiary: "#ffbcb7",
        "tertiary-container": "#ff938c",
        error: "#ffb4ab",
        "error-container": "#93000a",
      },
      fontFamily: {
        sans: ["Geist", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
