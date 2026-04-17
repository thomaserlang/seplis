import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { Flex } from '@mantine/core'
import { useGetSeries } from '../api/series.api'
import { SeriesView } from './series-view'

interface Props {
    seriesId: number
}

export function SeriesContainer({ seriesId }: Props) {
    const { data, isLoading, error } = useGetSeries({
        seriesId,
    })

    return (
        <>
            {isLoading && (
                <Flex
                    justify="center"
                    align="center"
                    style={{ height: '50dvh' }}
                >
                    <PageLoader />
                </Flex>
            )}
            {error && !data && <ErrorBox errorObj={error} />}
            {data && <SeriesView series={data} />}
        </>
    )
}
