import { createBrowserRouter } from 'react-router-dom'

export const router = createBrowserRouter([
    {
        path: '/',
        element: <div>Home</div>,
    },
    {
        path: '/login',
        lazy: () => import('./features/login/login.page'),
    },
    {
        path: '/request-reset-password',
        lazy: () => import('./features/login/request-reset-password.page'),
    },
    {
        path: '/users/reset-password/:key',
        lazy: () => import('./features/login/reset-password.page'),
    },
])
