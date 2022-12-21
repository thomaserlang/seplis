import React from 'react'
import { BrowserRouter, createBrowserRouter, Route, RouterProvider, Routes } from 'react-router-dom'
import { createRoot } from 'react-dom/client'
import { QueryClient } from '@tanstack/react-query'
import { ChakraProvider, extendTheme, type ThemeConfig } from '@chakra-ui/react'

import Login from './viewes/login'
import { QueryParamProvider } from 'use-query-params'
import { ReactRouter6Adapter } from 'use-query-params/adapters/react-router-6'

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: false,
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

createRoot(document.getElementById("root")).render(
    <React.StrictMode>
        <ChakraProvider theme={theme}>
            <BrowserRouter>
                <QueryParamProvider adapter={ReactRouter6Adapter}>
                    <Routes>
                        <Route path="/" element={<div>test</div>} /> 
                        <Route path="/login" element={<Login />} />
                    </Routes>
                </QueryParamProvider>
            </BrowserRouter>
        </ChakraProvider>
    </React.StrictMode>
)