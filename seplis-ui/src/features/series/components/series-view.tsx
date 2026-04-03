import { Flex } from '@mantine/core'
import { Series } from '../types/series.types'
import { SeriesInfo } from './series-info'

interface Props {
    series: Series
}

export function SeriesView({ series }: Props) {
    return (
        <Flex direction="column" gap="0.5rem">
            <SeriesInfo series={series} />
        </Flex>
    )
}
