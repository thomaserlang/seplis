import { Button, ButtonGroup } from '@chakra-ui/react'
import { FaPlay } from 'react-icons/fa'
import { PlayButtonMenu } from './play-button-menu'

interface IProps {
    playServersUrl: string,
    isLoading?: boolean,
    onPlayClick: () => void,
}

export function PlayButton({ onPlayClick, playServersUrl, isLoading }: IProps) {
    return <ButtonGroup isAttached>
        <Button
            leftIcon={<FaPlay />}
            onClick={onPlayClick}
            isLoading={isLoading}
        >
            Play
        </Button>
        <PlayButtonMenu
            playServersUrl={playServersUrl}
        />
    </ButtonGroup>
}