import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'node:url'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const envDir = fileURLToPath(new URL('.', import.meta.url))
  const env = loadEnv(mode, envDir, '')

  const host = env.VITE_DEV_SERVER_HOST || '0.0.0.0'
  const port = Number.parseInt(env.VITE_DEV_SERVER_PORT || '5173', 10)

  return {
    plugins: [react()],
    server: {
      host,
      port: Number.isNaN(port) ? 5173 : port,
      allowedHosts: true,
    },
  }
})
