import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: process.env.NODE_ENV === 'production' ? '/park/' : '/',
  build: {
    outDir: '../dist'
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Flask backend
        changeOrigin: true,
        // REMOVE or comment out the rewrite line!
        // rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})