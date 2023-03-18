import { setTitle } from '@seplis/utils'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { MovieLoad } from '@seplis/components/movie/movie'
import { Box, Modal, ModalBody, ModalCloseButton, ModalContent, ModalOverlay } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'


export default function MoviePage() {
    const { movieId } = useParams()

    return <>
        <MainMenu active="movies" />
        <Box margin="1rem">
            <MovieLoad movieId={parseInt(movieId)} onLoaded={(movie) => {
                setTitle(movie.title)
            }} />
        </Box>
    </>
}


export function MovieModalPage() {
    const { movieId } = useParams()
    const navigate = useNavigate()
    const location = useLocation()

    return <Modal
        isOpen={true}
        onClose={() => {
            navigate(location.state?.background?.pathname || '/')
        }}
        autoFocus={true}
    >
        <ModalOverlay />
        <ModalContent layerStyle="baseModal">
            <ModalCloseButton />
            <ModalBody>
                <MovieLoad movieId={parseInt(movieId)} onLoaded={(movie) => {
                    setTitle(movie.title)
                }} />
            </ModalBody>
        </ModalContent>
    </Modal>
}