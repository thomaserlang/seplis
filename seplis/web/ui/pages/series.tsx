import { Box, Modal, ModalBody, ModalCloseButton, ModalContent, ModalOverlay } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import { SeriesLoad } from '@seplis/components/series/series'
import { setTitle } from '@seplis/utils'
import { useLocation, useNavigate, useParams } from 'react-router-dom'

export default function SeriesPage() {
    const { seriesId } = useParams()

    return <>
        <MainMenu active="series" />
        <Box margin='1rem'>
            <SeriesLoad seriesId={parseInt(seriesId)} onLoaded={(series) => {
                setTitle(series.title)
            }} />
        </Box>
    </>
}


export function SeriesModalPage() {
    const { seriesId } = useParams()
    const navigate = useNavigate()
    const location = useLocation()

    return <>
        <Modal isOpen={true} onClose={() => {
            navigate(location.state?.background?.pathname || '/')
        }}>
            <ModalOverlay />
            <ModalContent layerStyle="baseModal">
                <ModalCloseButton />
                <ModalBody>
                    <SeriesLoad seriesId={parseInt(seriesId)} onLoaded={(series) => {
                        setTitle(series.title)
                    }} />
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}