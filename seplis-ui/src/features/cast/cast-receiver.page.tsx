import { MantineProvider } from '@mantine/core'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/queryclient'
import { theme } from '@/theme'
import { CastReceiver } from './components/cast-receiver'

// This page is loaded by the Chromecast device as the custom receiver app.
// It must NOT include the main shell navigation.
export function Component() {
    return (
        <MantineProvider theme={theme} forceColorScheme="dark">
            <QueryClientProvider client={queryClient}>
                <CastReceiver />
            </QueryClientProvider>
        </MantineProvider>
    )
}
