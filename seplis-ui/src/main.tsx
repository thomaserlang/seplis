import { MantineProvider } from '@mantine/core'
import { Notifications } from '@mantine/notifications'
import { QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { queryClient } from './queryclient'
import { router } from './router'

import { theme } from './theme'
import './theme.css'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
    <React.StrictMode>
        <MantineProvider theme={theme} forceColorScheme={'dark'}>
            <Notifications position="top-right" />
            <QueryClientProvider client={queryClient}>
                <RouterProvider router={router} />
            </QueryClientProvider>
        </MantineProvider>
    </React.StrictMode>,
)

window.addEventListener('vite:preloadError', () => {
    const lastReload = Number(sessionStorage.getItem('vite-last-reload') || 0)
    const now = Date.now()

    if (now - lastReload < 30_000) return

    sessionStorage.setItem('vite-last-reload', String(now))
    window.location.reload()
})
