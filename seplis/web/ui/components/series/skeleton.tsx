import { Box, Flex, Skeleton } from "@chakra-ui/react"

export default function SeriesSkeleton() {
    return <Flex direction="column" gap="1rem" maxWidth="1075px">
        <Flex gap="1rem">
            <Box className="poster-container-sizing">
                <Box className="poster-container" flexShrink="1">
                    <Skeleton height="100%" borderRadius="md" />
                </Box>
            </Box>
            <Flex gap="0.5rem" direction="column" basis="800px" grow="1" maxWidth="800px">
                <Skeleton height="40px" borderRadius="md" />
                <Skeleton flex="1 1 auto" borderRadius="md" />
            </Flex>
        </Flex>
        <Skeleton height="120px" borderRadius="md" />
    </Flex>
}