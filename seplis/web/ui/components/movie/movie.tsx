import { StarIcon } from '@chakra-ui/icons'
import { Box, Button, Flex, Heading, HStack, Icon, Link, Modal, ModalBody, ModalCloseButton, ModalContent, ModalHeader, ModalOverlay, Tag, useDisclosure } from '@chakra-ui/react'
import { IMovie } from '@seplis/interfaces/movie'
import { Poster } from '../poster'
import { langCodeToLang, secondsToHourMin } from '../../utils'
import StaredButton from './stared-button'
import { IGenre } from '@seplis/interfaces/genre'
import { FaCog, FaPlay } from 'react-icons/fa'
import Settings from './settings'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { useEffect } from 'react'
import { focusedBorder } from '@seplis/styles'
import PlayButton from './play-button'

interface IProps {
    movie: IMovie
}

export default function Movie({ movie }: IProps) {
    const { ref, focusKey, setFocus } = useFocusable()

    useEffect(() => {
        setFocus('MOVIE_PLAY')
    }, [])

    return <FocusContext.Provider value={focusKey}>
        <Flex>
            <MoviePoster movie={movie} />
            <Box marginLeft="1rem" maxWidth="800px" ref={ref}>
                <Title movie={movie} />

                <Box marginTop="0.5rem">
                    <BaseInfo movie={movie} />
                </Box>

                <Box marginTop="0.5rem">
                    <Genres genres={movie.genres} />
                </Box>

                <Box marginTop="1rem">
                    <Buttons movie={movie} />
                </Box>

                <Box marginTop="1rem">
                    <Plot movie={movie} />
                </Box>

                <Box marginTop="0.5rem">
                    <ExternalLinks movie={movie} />
                </Box>

            </Box>
        </Flex>
    </FocusContext.Provider>
}

function Buttons({ movie }: { movie: IMovie }) {
    return <HStack spacing="0.5rem" wrap="wrap">
        <PlayButton movieId={movie.id} />
        <StaredButton movieId={movie.id} />
        <DisplaySettings movie={movie} />
    </HStack>
}

function Genres({ genres }: { genres: IGenre[] }) {
    return <HStack spacing="0.5rem" wrap="wrap">
        {genres.map(genre => (
            <Genre key={genre.id} genre={genre} />
        ))}
    </HStack>
}

function Genre({ genre }: { genre: IGenre }) {
    const { ref, focused } = useFocusable()
    return <Tag
        ref={ref}
        style={focused ? focusedBorder : {}}
    >
        {genre.name}
    </Tag>
}

function BaseInfo({ movie }: { movie: IMovie }) {
    return <HStack spacing="0.5rem" wrap="wrap">
        {movie.release_date && <div><strong title={movie.release_date}>{movie.release_date.substring(0, 4)}</strong></div>}
        {movie.runtime && <div>{secondsToHourMin(movie.runtime)}</div>}
        {movie.language && <div>{langCodeToLang(movie.language)}</div>}
        {movie.rating && <div title="IMDb rating">{movie.rating} <StarIcon boxSize={2} /></div>}
    </HStack>
}

function Plot({ movie }: { movie: IMovie }) {
    if (!movie.plot)
        return
    return <Box>
        <Box><strong>Plot</strong></Box>
        <Box>{movie.plot}</Box>
    </Box>
}

function Title({ movie }: { movie: IMovie }) {
    return <Box>
        <Heading as="h1">{movie.title || '<Missing title>'}</Heading>
        {movie.original_title != movie.title &&
            <Heading as="h2" fontSize="1.5rem" color="RGBA(255, 255, 255, 0.36)">{movie.original_title}</Heading>}

        {movie.tagline && <div><i>{movie.tagline}</i></div>}
    </Box>
}

function MoviePoster({ movie }: { movie: IMovie }) {
    return <div className="poster-container-sizing">
        <div className="poster-container" style={{ 'flexShrink': '0' }}>
            <Poster url={`${movie.poster_image?.url}@SX320.webp`} title={movie.title} />
        </div>
    </div>
}

function ExternalLinks({ movie }: { movie: IMovie }) {
    if (!movie.externals.imdb || !movie.externals.themoviedb)
        return
    return <HStack spacing="0.5rem">
        {movie.externals.imdb && <Link href={`https://imdb.com/title/${movie.externals.imdb}`} isExternal>IMDb</Link>}
        {movie.externals.themoviedb && <Link href={`https://www.themoviedb.org/movie/${movie.externals.themoviedb}`} isExternal>TheMovieDB</Link>}
    </HStack>
}

function DisplaySettings({ movie }: { movie: IMovie }) {
    const { isOpen, onOpen, onClose } = useDisclosure()
    const { ref, focused } = useFocusable({
        onEnterPress: () => onOpen()
    })

    return <>
        <Button
            ref={ref}
            onClick={onOpen}
            leftIcon={<FaCog />}
            style={focused ? focusedBorder : null}
        >
            Settings
        </Button>

        <Modal onClose={onClose} isOpen={isOpen}>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>{movie.title} - Settings</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <Box marginBottom="1rem">
                        <Settings movie={movie} />
                    </Box>
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}