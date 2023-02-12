import { Box, Flex, Text } from "@chakra-ui/react";
import { IEpisode } from "@seplis/interfaces/episode";
import { EpisodeAirdate, episodeNumber } from "@seplis/utils";
import { PlayButton } from "./episode-play-button";
import WatchedButton from "./episode-watched-button";

export default function EpisodeCard({ seriesId, episode }: { seriesId: number, episode: IEpisode }) {
    return <Flex 
        backgroundColor="blackAlpha.500" 
        padding="0.5rem" 
        gap="0.5rem" 
        direction="column" 
        rounded="md"
        width="100%"
    >
        <Text noOfLines={1} lineHeight="1">{episode.title}</Text>        
        <Text noOfLines={1} lineHeight="1">{episodeNumber(episode)} · {EpisodeAirdate(episode)}</Text>
        <Flex gap="0.5rem">
            <WatchedButton seriesId={seriesId} data={episode.user_watched} />
            <Box marginLeft="auto"><PlayButton seriesId={seriesId} episode={episode} /></Box>
        </Flex>
    </Flex>
}