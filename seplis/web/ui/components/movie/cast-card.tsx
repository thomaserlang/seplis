import { Text, Flex, Box, Skeleton } from '@chakra-ui/react'
import { IMovieCastPerson } from '@seplis/interfaces/movie-cast'
import { PosterAspectRatio } from '../poster'

export default function CastCard({ castPerson }: { castPerson: IMovieCastPerson }) {
    return <Flex gap="0.5rem" layerStyle="episodeCard">
        <Box width="70px" rounded="md" overflow="hidden">
            <PosterAspectRatio
                url={castPerson.person.profile_image?.url+'@SX70.webp'}
                title={castPerson.person.name}
            />
        </Box>
        <Flex direction="column" gap="0.25rem">
            <Text fontWeight="600" lineHeight="0.7rem">{castPerson.person.name}</Text>
            <Text>{castPerson.character}</Text>
        </Flex>
    </Flex>
}

export function CastCardSkeleton() {
    return <Flex gap="0.5rem" layerStyle="episodeCard">
        <Box width="70px" rounded="md" overflow="hidden">            
            <Skeleton aspectRatio={603/887} />
        </Box>
        <Flex direction="column" gap="0.25rem">
            <Skeleton height="20px" width="175px" />
            <Skeleton height="20px" width="150px" />
        </Flex>
    </Flex>
}