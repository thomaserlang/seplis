import { mediaTypes } from '@/features/media-type'
import { Modal } from '@mantine/core'
import { useMediaQuery } from '@mantine/hooks'
import { useSearchParams } from 'react-router-dom'

export function MainModalDisplay() {
    const [params, setParams] = useSearchParams()

    const mid = params.get('mid')

    const [type, id] = mid?.split('-') ?? []
    const isMobile = useMediaQuery('(max-width: 48em)')

    const Container = mediaTypes[type as keyof typeof mediaTypes]?.render

    return (
        <Modal
            opened={!!Container}
            onClose={() => {
                setParams((params) => {
                    params.delete('mid')
                    return params
                })
            }}
            size={1100}
            fullScreen={isMobile}
            styles={{
                header: {
                    position: 'absolute',
                    top: -5,
                    right: 0,
                    background: 'transparent',
                    zIndex: 10,
                },
                body: { padding: 0 },
                content: { overflowX: 'hidden', overflowY: 'auto' },
            }}
        >
            {Container && <Container itemId={id} />}
        </Modal>
    )
}
