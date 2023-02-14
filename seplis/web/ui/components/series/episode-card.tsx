import { Box, Flex, Stack, Text } from '@chakra-ui/react'
import { IEpisode } from '@seplis/interfaces/episode'
import { EpisodeAirdate, episodeNumber } from '@seplis/utils'
import { PlayButton } from './episode-play-button'
import WatchedButton from './episode-watched-button'

export default function EpisodeCard({ seriesId, episode }: { seriesId: number, episode: IEpisode }) {
    return <Flex 
        direction="column"
        grow="1"
        basis="300px"
        layerStyle="episodeCard"
    >
        <Stack spacing="0.4rem">
            <Text noOfLines={1} lineHeight="1.3">{episode.title}</Text>        
            <Text noOfLines={1} lineHeight="1.3">{episodeNumber(episode)} · {EpisodeAirdate(episode)}</Text>
            <Stack direction="row">
                <WatchedButton seriesId={seriesId} episodeNumber={episode.number} data={episode.user_watched} />
                <Box marginLeft="auto"><PlayButton seriesId={seriesId} episodeNumber={episode.number} canPlay={episode.user_can_watch?.on_play_server} /></Box>
            </Stack>
        </Stack>
    </Flex>
}