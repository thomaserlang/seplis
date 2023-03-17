import { Box, Flex, Stack, Text } from '@chakra-ui/react'
import { IEpisode } from '@seplis/interfaces/episode'
import { EpisodeAirdate, episodeNumber } from '@seplis/utils'
import { ReactNode } from 'react'
import { PlayButton } from './episode-play-button'
import EpisodeWatchedButton from './episode-watched-button'

export default function EpisodeCard({ seriesId, episode }: { seriesId: number, episode: IEpisode }) {
    return <EpisodeCardWrapper>
        <Text noOfLines={1} lineHeight="1.3">{episode.title}</Text>        
        <Text noOfLines={1} lineHeight="1.3">{episodeNumber(episode)} · {EpisodeAirdate(episode)}</Text>
        <Flex>
            <EpisodeWatchedButton seriesId={seriesId} episodeNumber={episode.number} data={episode.user_watched} />
            <Box marginLeft="auto"><PlayButton seriesId={seriesId} episodeNumber={episode.number} canPlay={episode.user_can_watch?.on_play_server} /></Box>
        </Flex>
    </EpisodeCardWrapper>
}

export function EpisodeCardWrapper({ children }: { children: ReactNode }) {
    return <Flex 
        direction="column"
        grow="1"
        layerStyle="episodeCard"
        align="stretch"
        gap="0.4rem"
    >
        {children}
    </Flex>
}