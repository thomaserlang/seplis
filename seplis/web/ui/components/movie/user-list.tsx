import { Box, Modal, ModalBody, ModalCloseButton, ModalContent, ModalOverlay, useDisclosure } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import ImageList from '@seplis/components/list'
import { IMovie, IMovieUser } from '@seplis/interfaces/movie'
import { useEffect, useState } from 'react'
import { NumberParam, StringParam, useQueryParams, withDefault } from 'use-query-params'
import Movie from './movie'
import { MovieUserFilter } from './user-filter'


export default function MovieUserList({ title, url }: { title: string, url: string }) {
    const { ref, focusKey, focusSelf } = useFocusable()
    const { isOpen, onOpen, onClose } = useDisclosure()
    const [movie, setMovie] = useState<IMovie>(null)

    const [query, setQuery] = useQueryParams({
        sort: withDefault(StringParam, ""),
        genre_id: withDefault(NumberParam, 0),
    })

    useEffect(() => {
        focusSelf()
    }, [focusSelf])

    return <>
        <FocusContext.Provider value={focusKey}>
            <Box ref={ref}>
                <ImageList<IMovieUser>
                    title={title}
                    url={url}
                    urlParams={{
                        ...query,
                        'per_page': 50,
                    }}
                    parseItem={(item) => (
                        {
                            key: `movie-${item.movie.id}`,
                            title: item.movie.title,
                            img: item.movie.poster_image?.url,
                        }
                    )}
                    onItemSelected={(item: IMovieUser) => {
                        setMovie(item.movie)
                        onOpen()
                    }}
                    renderFilter={(options) => {
                        return <MovieUserFilter defaultValue={query} onSubmit={(data) => {
                            setQuery(data)
                            options.onClose()
                        }} />
                    }}
                />
            </Box>
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
