import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/gradio': {
        target: 'http://127.0.0.1:7860',
        changeOrigin: true,
        // Gradio uses relative asset paths; proxy websockets too if needed
        ws: true,
      },
    },
  },
})
