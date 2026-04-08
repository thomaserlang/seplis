import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '')

    return {
        plugins: [react()],
        server: {
            allowedHosts: true,
            proxy: {
                '^/api/.*': {
                    target: env.VITE_API_URL || 'http://127.0.0.1:8002',
                    secure: false,
                    changeOrigin: true,
                    rewrite: (path) => path.replace(/^\/api/, ''),
                },
            },
        },
        resolve: {
            dedupe: ['react', 'react-dom'],
            tsconfigPaths: true,
            alias: {
                '@': '/src',
            },
        },
    }
})
