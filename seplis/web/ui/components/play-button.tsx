import { Button, ButtonGroup } from '@chakra-ui/react'
import { FaPlay } from 'react-icons/fa'
import { PlayButtonMenu } from './play-button-menu'

interface IProps {
    playServersUrl: string,
    onPlayClick: () => void,
}

export function PlayButton({ onPlayClick, playServersUrl }: IProps) {
    return <ButtonGroup isAttached>
        <Button
            leftIcon={<FaPlay />}
            onClick={onPlayClick}
        >
            Play
        </Button>
        <PlayButtonMenu
            playServersUrl={playServersUrl}
        />
    </ButtonGroup>
}