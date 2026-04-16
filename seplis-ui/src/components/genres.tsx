import { Genre } from '@/features/genres/types/genre.types'
import { Flex, Text } from '@mantine/core'

interface Props extends Text.Props {
    genres?: Genre[]
}

export function Genres({ genres, ...props }: Props) {
    if (!genres || genres.length === 0) return null

    return (
        <Flex columnGap="0.35rem" rowGap="0" wrap="wrap" align="center">
            {genres.flatMap((g, i) => [
                i > 0 ? (
                    <Text key={`dot-${g.id}`} {...props} c="dimmed">
                        ·
                    </Text>
                ) : null,
                <Text key={g.id} {...props} c="dimmed">
                    {g.name}
                </Text>,
            ])}
        </Flex>
    )
}
