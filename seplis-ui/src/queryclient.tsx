import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: (failureCount, error: any) => {
                const status = error?.response?.status
                if (status >= 500) {
                    return failureCount < 3
                }

                return false
            },
        },
    },
})
