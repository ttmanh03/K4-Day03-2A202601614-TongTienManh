import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Bind ra tất cả interface (0.0.0.0) để ngrok/LAN truy cập được,
    // mặc định Vite chỉ nghe trên localhost.
    host: true,
    // Cho phép Host header lạ (ngrok, cloudflare tunnel...), nếu không
    // Vite trả "Blocked request. This host is not allowed".
    allowedHosts: true,
    proxy: {
      // Backend FastAPI chạy ở 8001 (8000 dành cho server.py của Role 1)
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
})
