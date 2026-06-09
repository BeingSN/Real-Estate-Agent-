export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: { DEFAULT: '#0F1C2E', light: '#1A2E47' },
        gold: { DEFAULT: '#C9A84C', light: '#E2C97E' }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif']
      }
    }
  },
  plugins: []
}
