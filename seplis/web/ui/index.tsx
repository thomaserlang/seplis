import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ChakraProvider, extendTheme, type ThemeConfig } from '@chakra-ui/react'

import './index.less'

import Login from './pages/login'
import Movie, { MovieModalPage } from './pages/movie'
import Series, { SeriesModalPage } from './pages/series'

import { QueryParamProvider } from 'use-query-params'
import { ReactRouter6Adapter } from 'use-query-params/adapters/react-router-6'

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: false,
            refetchOnWindowFocus: false,
            keepPreviousData: true,
        },
    },
})

const config: ThemeConfig = {
    initialColorMode: 'dark',
    useSystemColorMode: false,
}

const theme = extendTheme({
    config: config,
    colors: {
        seplis: {
            100: '#36c',
            'modalBackgroundColor': '#1b1b1b',
        },
    },
    components: {
        Popover: {
            variants: {
                responsive: {
                    content: { width: "unset" },
                },
            },
        },
        Button: {
            variants: {
                playButton: {
                    backgroundColor: '#000',
                    fontSize: '42px',
                }
            }
        }
    },
    layerStyles: {
        episodeCard: {
            backgroundColor: 'blackAlpha.500',
            padding: '0.5rem',
            borderRadius: 'md',
        },
        baseModal: {
            maxWidth: '1100px',
            backgroundColor: 'seplis.modalBackgroundColor',
            padding: '1rem 0',
        }
    },
    textStyles: {
        h2: {
            fontSize: '1.25rem',
            fontWeight: '600',
        },
        selectedText: {
            fontWeight: 'bolder',
        },
    },

})

import { init as spatialInit } from '@noriginmedia/norigin-spatial-navigation'
import SeriesHome from './pages/series/home'
import SeriesBrowse from './pages/series/browse'
import SeriesWatchlist from './pages/series/watchlist'
import SeriesFavorites from './pages/series/favorites'
import SeriesWatched from './pages/series/watched'
import MoviesBrowse from './pages/movies/browse'
import MovieWatchlist from './pages/movies/watchlist'
import MovieFavorites from './pages/movies/favorites'
import MoviesWatched from './pages/movies/watched'
import PlayEpisode from './pages/series/play-episode'
import PlayMovie from './pages/movies/play'
import Signup from './pages/signup'
import { Logout } from './pages/logout'
import SendResetPassword from './pages/send-reset-password'
import ResetPassword from './pages/reset-password'
import WatchHome from './pages/watch/home'
import { CastProvider } from './components/player/react-cast-sender'
import SeriesCountdown from './pages/series/countdown'
import SeriesRecentlyAired from './pages/series/recently-aired'
import SeriesToWatch from './pages/series/series-to-watch'
import { StrictMode } from 'react'

spatialInit({})

createRoot(document.getElementById("root")).render(
    <StrictMode>
        <ChakraProvider theme={theme}>
            <BrowserRouter >
                <QueryParamProvider adapter={ReactRouter6Adapter}>
                    <QueryClientProvider client={queryClient}>
                        <CastProvider receiverApplicationId={(window as any).seplisChromecastAppId}>
                            <App />
                        </CastProvider>
                    </QueryClientProvider>
                </QueryParamProvider>
            </BrowserRouter>
        </ChakraProvider>
    </StrictMode>
)

function App() {
    const location = useLocation()
    const background = location.state?.background
    return <>
        <Routes location={background || location}>
            <Route path="/" element={<WatchHome />} />
            <Route path="/login" element={<Login />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/users/reset-password" element={<SendResetPassword />} />
            <Route path="/users/reset-password/:key" element={<ResetPassword />} />
            <Route path="/movies" element={<MoviesBrowse />} />
            <Route path="/movies/watchlist" element={<MovieWatchlist />} />
            <Route path="/movies/favorites" element={<MovieFavorites />} />
            <Route path="/movies/watched" element={<MoviesWatched />} />
            <Route path="/movies/:movieId" element={<Movie />} />
            <Route path="/movies/:movieId/play" element={<PlayMovie />} />
            <Route path="/series" element={<SeriesBrowse />} />
            <Route path="/series/home" element={<SeriesHome />} />
            <Route path="/series/watchlist" element={<SeriesWatchlist />} />
            <Route path="/series/favorites" element={<SeriesFavorites />} />
            <Route path="/series/watched" element={<SeriesWatched />} />
            <Route path="/series/countdown" element={<SeriesCountdown />} />
            <Route path="/series/recently-aired" element={<SeriesRecentlyAired />} />
            <Route path="/series/to-watch" element={<SeriesToWatch />} />
            <Route path="/series/:seriesId" element={<Series />} />
            <Route path="/series/:seriesId/episodes/:episodeNumber/play" element={<PlayEpisode />} />
            <Route path="/watch" element={<WatchHome />} />
        </Routes>
        {background && <Routes>
            <Route path="/series/:seriesId" element={<SeriesModalPage />} />
            <Route path="/movies/:movieId" element={<MovieModalPage />} />
        </Routes>}
    </>
}