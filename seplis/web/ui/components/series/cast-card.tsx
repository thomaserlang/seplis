import { Text, Flex, Box, Skeleton } from '@chakra-ui/react'
import { ISeriesCastPerson } from '@seplis/interfaces/series-cast'
import { PosterAspectRatio } from '../poster'

export default function CastCard({ castPerson }: { castPerson: ISeriesCastPerson }) {
    return <Flex gap="0.5rem" layerStyle="episodeCard">
        <Box width="70px" rounded="md" overflow="hidden">
            <PosterAspectRatio
                url={castPerson.person.profile_image?.url+'@SX140.webp'}
                title={castPerson.person.name}
            />
        </Box>
        <Flex direction="column" gap="0.25rem">
            <Text fontWeight="600" lineHeight="0.7rem">{castPerson.person.name}</Text>
            {castPerson.roles.map(role => (
                <Text key={role.character}>{role.character}</Text>
            ))}
            <Text>{castPerson.total_episodes} {castPerson.total_episodes == 1 ? 'episode' : 'episodes'}</Text>
        </Flex>
    </Flex>
}

export function CastCardSkeleton() {
    return <Flex gap="0.5rem" layerStyle="episodeCard">
        <Box width="70px" rounded="md" overflow="hidden">            
            <Skeleton />
        </Box>
        <Flex direction="column" gap="0.25rem">
            <Skeleton height="20px" width="175px" />
            <Skeleton height="20px" width="150px" />
        </Flex>
    </Flex>
}