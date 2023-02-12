import { Flex, Skeleton } from '@chakra-ui/react'


export default function EpisodeSkeleton() {
    return <Flex
        width="100%"
        height="104px"
        grow="1"
        basis="300px"
        layerStyle="episodeCard"
    >
        <Skeleton height="100%" width="100%" />
    </Flex>
}