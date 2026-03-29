import api from '@/api'
import {
    EVENT_EPISODE_WATCHED,
    TriggerEpisodeWatched,
    useEventListener,
} from '@/events'
import {
    IEpisodeWatched,
    IEpisodeWatchedDefault,
    IEventEpisodeWatched,
} from '@/interfaces/episode'
import { useToast } from '@chakra-ui/react'
import { useEffect, useState } from 'react'
import { ErrorMessageFromResponse } from '../error'
import { WatchedButton } from '../watched-button'

export default function EpisodeWatchedButton({
    seriesId,
    episodeNumber,
    data,
}: {
    seriesId: number
    episodeNumber: number
    data?: IEpisodeWatched
}) {
    if (!data) data = IEpisodeWatchedDefault(0)
    const toast = useToast()
    const [watched, setWatched] = useState<IEpisodeWatched>(data)
    const [isUpdating, setUpdating] = useState(false)

    useEventListener<IEventEpisodeWatched>(
        EVENT_EPISODE_WATCHED,
        (data) => {
            if (
                data.seriesId == seriesId &&
                data.episodeNumber == episodeNumber
            )
                setWatched({ ...data.watched })
        },
        [seriesId, episodeNumber],
    )

    useEffect(() => {
        if (data != watched) setWatched({ ...data })
    }, [data])

    const increment = async () => {
        try {
            setUpdating(true)
            const r = await api.post<IEpisodeWatched>(
                `/2/series/${seriesId}/episodes/${episodeNumber}/watched`,
            )
            TriggerEpisodeWatched(seriesId, episodeNumber, r.data)
        } catch (e) {
            toast({
                title: ErrorMessageFromResponse(e),
                status: 'error',
                isClosable: true,
                position: 'top',
            })
        } finally {
            setUpdating(false)
        }
    }

    const decrement = async () => {
        try {
            setUpdating(true)
            const r = await api.delete(
                `/2/series/${seriesId}/episodes/${episodeNumber}/watched`,
            )
            TriggerEpisodeWatched(seriesId, episodeNumber, r.data)
        } catch (e) {
            toast({
                title: ErrorMessageFromResponse(e),
                status: 'error',
                isClosable: true,
                position: 'top',
            })
        } finally {
            setUpdating(false)
        }
    }

    return (
        <WatchedButton
            times={watched.times}
            position={watched.position}
            onIncrement={increment}
            onDecrement={decrement}
            isUpdating={isUpdating}
        />
    )
}
