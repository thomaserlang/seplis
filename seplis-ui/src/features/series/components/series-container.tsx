import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
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
            {isLoading && <PageLoader />}
            {error && !data && <ErrorBox errorObj={error} />}
            {data && <SeriesView series={data} />}
        </>
    )
}
