/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#080c14",
        surface: "#0f172a",
        surfaceBorder: "#1e293b",
        primary: "#8b5cf6",
        primaryHover: "#7c3aed",
        accent: "#ec4899",
        success: "#10b981",
        warning: "#f59e0b"
      },
    },
  },
  plugins: [],
}
