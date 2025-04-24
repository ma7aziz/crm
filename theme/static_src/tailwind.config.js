/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // New primary teal color (#1d9d86) and its shades
        'primary': {
          50: '#e6f5f2',
          100: '#cceae6',
          200: '#99d5cc',
          300: '#66c1b3',
          400: '#33ac99',
          500: '#1d9d86', // Base color
          600: '#177d6b',
          700: '#115e50',
          800: '#0c3e36',
          900: '#061f1b',
        },
        // New secondary blue color (#0088cc) and its shades
        'secondary': {
          50: '#e6f5fc',
          100: '#ccebf9',
          200: '#99d7f2',
          300: '#66c3ec',
          400: '#33afe5',
          500: '#0088cc', // Base color
          600: '#006da3',
          700: '#00527a',
          800: '#003652',
          900: '#001b29',
        },
        // New danger red color (#d20120) and its shades
        'danger': {
          50: '#fce6e9',
          100: '#f9ccd3',
          200: '#f299a7',
          300: '#ec667a',
          400: '#e5334e',
          500: '#d20120', // Base color
          600: '#a8011a',
          700: '#7e0114',
          800: '#54000d',
          900: '#2a0007',
        },
      },
    },
  },
  plugins: [],
}