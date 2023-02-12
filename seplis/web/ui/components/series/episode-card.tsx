import { Box, Flex, Text } from "@chakra-ui/react";
import { IEpisode } from "@seplis/interfaces/episode";
import { EpisodeAirdate, episodeNumber } from "@seplis/utils";
import { PlayButton } from "./episode-play-button";
import WatchedButton from "./episode-watched-button";

export default function EpisodeCard({ seriesId, episode }: { seriesId: number, episode: IEpisode }) {
    return <Flex 
        gap="0.5rem"
        direction="column"
        grow="1"
        basis="300px"
        layerStyle="episodeCard"
    >
        <Text noOfLines={1} lineHeight="1">{episode.title}</Text>        
        <Text noOfLines={1} lineHeight="1">{episodeNumber(episode)} · {EpisodeAirdate(episode)}</Text>
        <Flex gap="0.5rem">
            <WatchedButton seriesId={seriesId} episodeNumber={episode.number} data={episode.user_watched} />
            <Box marginLeft="auto"><PlayButton seriesId={seriesId} episodeNumber={episode.number} canPlay={episode.user_can_watch?.on_play_server} /></Box>
        </Flex>
    </Flex>
}