import { Flex, Skeleton } from '@chakra-ui/react'


export default function EpisodeSkeleton() {
    return <Flex
        backgroundColor="blackAlpha.500"
        rounded="md"
        width="100%"
        height="104px"
        grow="1"
        basis="300px"
    >
        <Skeleton height="100%" width="100%" />
    </Flex>
}