import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { Modal } from '@mantine/core'
import { useGetSeries } from '../api/series.api'
import { SeriesView } from './series-view'

interface Props {
    seriesId: number
    onClose: () => void
    opened: boolean
}

export function SeriesModal({ seriesId, onClose, opened }: Props) {
    const { data, isLoading, error } = useGetSeries({
        seriesId,
        options: {
            enabled: opened,
        },
    })

    return (
        <Modal opened={opened} onClose={onClose} size="lg">
            {isLoading && <PageLoader />}
            {error && !data && <ErrorBox errorObj={error} />}
            {data && <SeriesView series={data} />}
        </Modal>
    )
}
