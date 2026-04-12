import { Genre } from '@/types/genre.types'
import { Flex, Text } from '@mantine/core'

interface Props extends Text.Props {
    genres?: Genre[]
}

export function Genres({ genres, ...props }: Props) {
    if (!genres || genres.length === 0) return null

    return (
        <Flex gap="0.35rem" wrap="wrap" align="center">
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
