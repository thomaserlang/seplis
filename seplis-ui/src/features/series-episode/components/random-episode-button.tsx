import { useActiveUser } from '@/features/user'
import { toastError } from '@/utils/toast'
import { Button } from '@mantine/core'
import { ShuffleIcon } from '@phosphor-icons/react'
import { useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useGetRandomPlayableEpisode } from '../api/random-episode.api'

interface Props {
    seriesId: number
    totalEpisodes: number
}

export function RandomEpisodeButton({ seriesId, totalEpisodes }: Props) {
    const [user] = useActiveUser()
    const [, setParams] = useSearchParams()
    const { refetch, isFetching } = useGetRandomPlayableEpisode({
        seriesId,
        options: { enabled: false, retry: false, gcTime: 0 },
    })
    const generation = useRef(0)

    useEffect(() => {
        return () => {
            generation.current += 1
        }
    }, [seriesId, user])

    if (!user || totalEpisodes <= 40) return null

    const playRandomEpisode = async () => {
        if (isFetching) return
        const currentGeneration = ++generation.current
        const { data: episode, error } = await refetch({ cancelRefetch: false })
        if (generation.current !== currentGeneration) return
        if (error) {
            toastError(error)
            return
        }
        if (!episode) {
            toastError(new Error('No aired episodes are available to play.'))
            return
        }
        setParams((params) => {
            const nextParams = new URLSearchParams(params)
            nextParams.set('pid', `episode-${seriesId}:${episode.number}`)
            nextParams.set('position', '0')
            return nextParams
        })
    }

    return (
        <Button
            variant="default"
            size="compact-md"
            leftSection={<ShuffleIcon />}
            loading={isFetching}
            onClick={playRandomEpisode}
        >
            Random episode
        </Button>
    )
}
