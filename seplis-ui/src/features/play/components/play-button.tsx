import { Button, ButtonProps } from '@mantine/core'
import { PlayIcon } from '@phosphor-icons/react'
import { PlayRequest } from '../types/play-source.types'
import { PlaySourceDownloadMenu } from './play-source-download-menu'

interface Props extends ButtonProps {
    playRequests: PlayRequest[]
    onClick?: () => void
}

export function PlayButton({ playRequests, ...props }: Props) {
    return (
        <Button.Group>
            <Button
                variant="default"
                size="compact-md"
                leftSection={<PlayIcon weight="fill" />}
                {...props}
            >
                Play
            </Button>
            {playRequests.length > 0 && (
                <PlaySourceDownloadMenu playRequests={playRequests} />
            )}
        </Button.Group>
    )
}
