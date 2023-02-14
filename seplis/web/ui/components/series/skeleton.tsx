import { Box, Skeleton, Stack } from "@chakra-ui/react"

export default function SeriesSkeleton() {
    return <Stack direction="column" spacing="1rem" maxWidth="1100px">
        <Stack direction="row" spacing="1rem">
            <Box className="poster-container-sizing">
                <Box className="poster-container" flexShrink="1">
                    <Skeleton height="100%" borderRadius="md" />
                </Box>
            </Box>
            <Stack spacing="0.5rem" direction="column" width="100%">
                <Skeleton height="40px" borderRadius="md" />
                <Skeleton flex="1 1 auto" borderRadius="md" />
            </Stack>
        </Stack>
        <Skeleton height="120px" borderRadius="md" />
    </Stack>
}