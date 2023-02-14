import { Flex, Skeleton, Stack } from '@chakra-ui/react'


export default function EpisodeSkeleton() {
    return <Flex
        width="100%"
        height="104px"
        grow="1"
        basis="300px"
        layerStyle="episodeCard"
    >
        <Stack spacing="0.4rem">
            <Skeleton height="20px" width="325px" />
            <Skeleton height="20px" width="222px" />
            <Skeleton height="30px" width="150px" />
        </Stack>
    </Flex>
}