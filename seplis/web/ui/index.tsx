import React from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ChakraProvider, extendTheme, type ThemeConfig } from '@chakra-ui/react'

import './index.less'

import Login from './pages/login'
import Home from './pages/home'
import Movie from './pages/movie'

import { QueryParamProvider } from 'use-query-params'
import { ReactRouter6Adapter } from 'use-query-params/adapters/react-router-6'

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: false,
            refetchOnWindowFocus: false,
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
    }
})

import { init as spatialInit } from '@noriginmedia/norigin-spatial-navigation'

spatialInit({})

createRoot(document.getElementById("root")).render(
    <React.StrictMode>
        <ChakraProvider theme={theme}>
            <BrowserRouter >
                <QueryParamProvider adapter={ReactRouter6Adapter}>
                    <QueryClientProvider client={queryClient}>
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/movies/:movieId" element={<Movie />} />
                        </Routes>
                    </QueryClientProvider>
                </QueryParamProvider>
            </BrowserRouter>
        </ChakraProvider>
    </React.StrictMode>
)