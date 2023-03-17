import { Skeleton, Stack } from '@chakra-ui/react'
import { EpisodeCardWrapper } from './episode-card'


export default function EpisodeSkeleton() {
    return <EpisodeCardWrapper>
        <Skeleton height="20px" width="325px" />
        <Skeleton height="20px" width="222px" />
        <Skeleton height="30px" width="150px" />
    </EpisodeCardWrapper>
}