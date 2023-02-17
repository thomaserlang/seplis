import { AddIcon, MinusIcon } from '@chakra-ui/icons'
import { Button, ButtonGroup, IconButton, Popover, PopoverContent, PopoverTrigger, Stack, useDisclosure, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { IEpisodeWatched, IEpisodeWatchedDefault, IEventEpisodeWatched } from '@seplis/interfaces/episode'
import { EVENT_EPISODE_WATCHED, TriggerEpisodeWatched, useEventListener } from '@seplis/events'
import { forwardRef, useEffect, useState } from 'react'
import { ErrorMessageFromResponse } from '../error'


export default function EpisodeWatchedButton({ seriesId, episodeNumber, data }: { seriesId: number, episodeNumber: number, data?: IEpisodeWatched }) {
    if (!data) data = IEpisodeWatchedDefault(0)
    const toast = useToast()
    const [watched, setWatched] = useState<IEpisodeWatched>({ ...data })
    const [isUpdating, setUpdating] = useState(false)
    const { onOpen, onClose, isOpen, onToggle } = useDisclosure()

    useEventListener<IEventEpisodeWatched>(EVENT_EPISODE_WATCHED, ((data) => {
        if ((data.seriesId == seriesId) && (data.episodeNumber == episodeNumber))
            setWatched({ ...data.watched })
    }), [])

    useEffect(() => {
        setWatched({ ...data })
    }, [data])

    const increment = async () => {
        try {
            setUpdating(true)
            const r = await api.post<IEpisodeWatched>(`/2/series/${seriesId}/episodes/${episodeNumber}/watched`)
            TriggerEpisodeWatched(seriesId, episodeNumber, r.data)
            if (r.data.times > 1)
                if (isOpen)
                    onToggle()
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
            const r = await api.delete(`/2/series/${seriesId}/episodes/${episodeNumber}/watched`)
            TriggerEpisodeWatched(seriesId, episodeNumber, r.data)
            if (isOpen)
                onToggle()
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

    return <>
        {watched.times == 0 && <BaseButton
            watched={watched}
            onClick={increment}
            isUpdating={isUpdating}
        />}

        {watched.times > 0 && <Popover
            isOpen={isOpen}
            onOpen={onOpen}
            onClose={onClose}
            placement='top'
            closeOnBlur={true}
            variant="responsive"
        >
            <PopoverTrigger>
                <BaseButton
                    watched={watched}
                    onClick={watched.times == 0 ? increment : null}
                    isUpdating={isUpdating}
                />
            </PopoverTrigger>
            <PopoverContent padding="0.5rem">
                <Stack direction="row">
                    <IconButton
                        colorScheme="red"
                        aria-label="Decrement watched"
                        icon={<MinusIcon />}
                        onClick={decrement}
                        isLoading={isUpdating}
                    />
                    <IconButton
                        colorScheme="green"
                        aria-label="Increment watched"
                        icon={<AddIcon />}
                        onClick={increment}
                        isLoading={isUpdating}
                    />
                </Stack>
            </PopoverContent>
        </Popover>}
    </>
}

interface IButton {
    watched: IEpisodeWatched,
    onClick?: () => void,
    isUpdating?: boolean,
}

const BaseButton = forwardRef<any, IButton>((props, ref) => {
    return <ButtonGroup ref={ref} isAttached variant='outline'>
        <Button
            colorScheme={props.watched.times > 0 ? "green" : null}
            variant={props.watched.times > 0 ? "solid" : 'outline'}
            style={props.watched.position > 0 ? {
                background: "linear-gradient(90deg, #428bca 56%, var(--chakra-colors-green-300) 44%)"
            } : null}
            onClick={props.onClick}
            isLoading={props.isUpdating}
        >
            Watched
        </Button>
        <Button onClick={props.onClick}>{props.watched.times}</Button>
    </ButtonGroup>
})