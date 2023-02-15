import { Modal, ModalBody, ModalCloseButton, ModalContent, ModalOverlay, Stack, useDisclosure } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import MainMenu from '@seplis/components/main-menu'
import Movie from '@seplis/components/movie/movie'
import Slider from '@seplis/components/slider'
import { IMovie, IMovieUser } from '@seplis/interfaces/movie'
import { setTitle } from '@seplis/utils'
import { useCallback, useEffect, useState } from 'react'


export default function MoviesHome() {
    const { ref, focusKey, focusSelf } = useFocusable()
    const { isOpen, onOpen, onClose } = useDisclosure()
    const [movie, setMovie] = useState<IMovie>(null)

    useEffect(() => {
        setTitle('Movies Home')
    }, [])

    useEffect(() => {
        focusSelf()
    }, [focusSelf])

    const onRowFocus = useCallback(({ y }: { y: number }) => {
        window.scrollTo({
            top: y,
            behavior: 'smooth'
        });
    }, [ref])

    const itemSelected = (item: IMovieUser) => {
        setMovie(item.movie)
        onOpen()
    }

    return <>
        <MainMenu />
        
        <FocusContext.Provider value={focusKey}>

            <Stack ref={ref} marginTop="0.5rem">

                <Slider<IMovieUser>
                    title="Watched"
                    url="/2/users/me/movies-watched"
                    parseItem={(item) => (
                        {
                            key: `movie-${item.movie.id}`,
                            title: item.movie.title,
                            img: item.movie.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={itemSelected}
                />

                <Slider<IMovieUser>
                    title="Stared"
                    url="/2/users/me/movies-stared"
                    parseItem={(item) => (
                        {
                            key: `movie-${item.movie.id}`,
                            title: item.movie.title,
                            img: item.movie.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={itemSelected}
                />

            </Stack>
        </FocusContext.Provider>

        <Modal isOpen={isOpen} onClose={onClose}>
            <ModalOverlay />
            <ModalContent maxWidth="1100px" backgroundColor="gray.900" padding="1rem 0">
                <ModalCloseButton />
                <ModalBody>
                    <Movie movie={movie} />
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}