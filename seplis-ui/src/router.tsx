import { Anchor, Center, Container, Text, Title } from '@mantine/core'
import {
    createBrowserRouter,
    isRouteErrorResponse,
    Outlet,
    useRouteError,
} from 'react-router-dom'
import { ErrorBox } from './components/error-box'
import { Logo } from './components/logo'
import { MainShell } from './features/main-shell/components/main-shell'

export const router = createBrowserRouter([
    {
        ErrorBoundary: () => {
            const error = useRouteError()

            if (isRouteErrorResponse(error)) {
                return (
                    <Container size="xs" pt="1rem">
                        <Center mb="2rem">
                            <Logo />
                        </Center>
                        <Title order={1}>{error.status}</Title>
                        <Text mb="1rem">{error.statusText}</Text>
                        <Anchor href="/">Go back</Anchor>
                    </Container>
                )
            }
            return (
                <Container pt="1rem">
                    <Center mb="2rem">
                        <Logo />
                    </Center>
                    <ErrorBox errorObj={error} />
                </Container>
            )
        },
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
    {
        path: '/cast-receiver',
        lazy: () => import('./features/cast/cast-receiver.page'),
    },
    {
        path: '/series/:seriesId/episodes/:episodeNumber/play',
        lazy: () => import('./features/series-episode/episode-play.page'),
    },
    {
        path: '/movies/:movieId/play',
        lazy: () => import('./features/movie/movie-play.page'),
    },
    {
        path: '/',
        element: (
            <MainShell>
                <Outlet />
            </MainShell>
        ),
    },
])
