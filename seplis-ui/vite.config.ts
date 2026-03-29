import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '^/api/.*': {
                target: 'http://127.0.0.1:8002',
                secure: false,
                rewrite: (path) => path.replace(/^\/api/, ''),
            },
        },
    },
    resolve: {
        tsconfigPaths: true,
    },
})
