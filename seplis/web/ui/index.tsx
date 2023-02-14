import React from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ChakraProvider, extendTheme, type ThemeConfig } from '@chakra-ui/react'

import './index.less'

import Login from './pages/login'
import Movie from './pages/movie'
import Series from './pages/series'

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
        }
    },
    components: {
        Popover: {
            variants: {
                responsive: {
                    content: { width: "unset" },
                },
            },
        },
    },
    layerStyles: {
        episodeCard: {
            backgroundColor: 'blackAlpha.500',
            padding: '0.5rem',
            borderRadius: 'md',
        }
    }
})

import { init as spatialInit } from '@noriginmedia/norigin-spatial-navigation'
import SeriesHome from './pages/series/home'
import MoviesHome from './pages/movies/home'

spatialInit({})

createRoot(document.getElementById("root")).render(
    <React.StrictMode>
        <ChakraProvider theme={theme}>
            <BrowserRouter >
                <QueryParamProvider adapter={ReactRouter6Adapter}>
                    <QueryClientProvider client={queryClient}>
                        <Routes>
                            <Route path="/" element={<SeriesHome />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/movies/home" element={<MoviesHome />} />
                            <Route path="/movies/:movieId" element={<Movie />} />
                            <Route path="/series/home" element={<SeriesHome />} />
                            <Route path="/series/:seriesId" element={<Series />} />
                        </Routes>
                    </QueryClientProvider>
                </QueryParamProvider>
            </BrowserRouter>
        </ChakraProvider>
    </React.StrictMode>
)