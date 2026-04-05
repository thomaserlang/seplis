import { Button, ButtonProps, ButtonSize } from '@mantine/core'
import { CaretDownIcon, PlayIcon } from '@phosphor-icons/react'
import { PlayRequest } from '../types/play-source.types'
import { PlaySourceDownloadMenu } from './play-source-download-menu'

interface Props extends ButtonProps {
    playRequests: PlayRequest[] | undefined
    getPlayRequests: () => void
    onClick?: () => void
    size?: ButtonSize
}

export function PlayButton({
    playRequests,
    getPlayRequests,
    size = 'compact-md',
    ...props
}: Props) {
    return (
        <Button.Group>
            <Button
                variant="default"
                size={size}
                leftSection={<PlayIcon weight="fill" />}
                {...props}
            >
                Play
            </Button>
            <PlaySourceDownloadMenu
                playRequests={playRequests}
                getPlayRequests={getPlayRequests}
            >
                <Button size={size} variant="default">
                    <CaretDownIcon weight="bold" />
                </Button>
            </PlaySourceDownloadMenu>
        </Button.Group>
    )
}
