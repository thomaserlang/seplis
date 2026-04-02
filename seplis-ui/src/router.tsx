import { createBrowserRouter } from 'react-router-dom'

export const router = createBrowserRouter([
    {
        path: '/',
        element: <div>Home</div>,
    },
    {
        path: '/login',
        lazy: () => import('./features/user/login.page'),
    },
    {
        path: '/request-reset-password',
        lazy: () => import('./features/user/request-reset-password.page'),
    },
    {
        path: '/users/reset-password/:key',
        lazy: () => import('./features/user/reset-password.page'),
    },
    {
        path: '/signup',
        lazy: () => import('./features/user/signup.page'),
    },
])
