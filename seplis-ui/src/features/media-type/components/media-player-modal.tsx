import { mediaTypes } from '@/features/media-type'
import { Modal } from '@mantine/core'
import { useSearchParams } from 'react-router-dom'

export function MediaPlayerModal() {
    const [params, setParams] = useSearchParams()

    const mid = params.get('pid')

    const [type, id] = mid?.split('-') ?? []

    const Player = mediaTypes[type as keyof typeof mediaTypes]?.player

    const closePlayer = () =>
        setParams((params) => {
            params.delete('pid')
            return params
        })

    return (
        <Modal
            opened={!!Player}
            trapFocus={true}
            autoFocus={true}
            onClose={closePlayer}
            fullScreen={true}
            withCloseButton={false}
            styles={{
                body: { padding: 0, height: '100%' },
                content: { display: 'flex', flexDirection: 'column' },
            }}
        >
            {Player && <Player itemId={id} onClose={closePlayer} />}
        </Modal>
    )
}
