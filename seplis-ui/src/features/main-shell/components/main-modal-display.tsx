import { mediaTypes } from '@/features/media-type'
import { Modal } from '@mantine/core'
import { useSearchParams } from 'react-router-dom'

export function MainModalDisplay() {
    const [params, setParams] = useSearchParams()

    const mid = params.get('mid')

    const [type, id] = mid?.split('-') ?? []

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
            styles={{
                header: {
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    background: 'transparent',
                    zIndex: 10,
                    padding: '0.5rem',
                },
                body: { padding: 0 },
                content: { overflow: 'hidden' },
            }}
        >
            {Container && <Container itemId={id} />}
        </Modal>
    )
}
