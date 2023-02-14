import { StarIcon } from '@chakra-ui/icons'
import { Text, Box, Button, Flex, Heading, Link, Modal, ModalBody, ModalCloseButton, ModalContent, ModalHeader, ModalOverlay, Tag, useDisclosure } from '@chakra-ui/react'
import { IMovie } from '@seplis/interfaces/movie'
import { Poster } from '../poster'
import { langCodeToLang, secondsToHourMin } from '../../utils'
import StaredButton from './stared-button'
import { IGenre } from '@seplis/interfaces/genre'
import { FaCog } from 'react-icons/fa'
import Settings from './settings'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { useEffect, useState } from 'react'
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
        <Flex gap="1rem">
            <MoviePoster movie={movie} />
            <Flex gap="0.5rem" direction="column" maxWidth="800px" ref={ref}>
                <Title movie={movie} />
                <BaseInfo movie={movie} />                
                <Genres genres={movie.genres} />
                <Buttons movie={movie} />
                <Plot movie={movie} />                
                <ExternalLinks movie={movie} />
            </Flex>
        </Flex>
    </FocusContext.Provider>
}

function Buttons({ movie }: { movie: IMovie }) {
    return <Flex gap="0.5rem" wrap="wrap" padding="0.25rem 0">
        <PlayButton movieId={movie.id} />
        <StaredButton movieId={movie.id} />
        <DisplaySettings movie={movie} />
    </Flex>
}

function Genres({ genres }: { genres: IGenre[] }) {
    return <Flex gap="0.5rem" wrap="wrap" padding="0.25rem 0">
        {genres.map(genre => (
            <Genre key={genre.id} genre={genre} />
        ))}
    </Flex>
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
    return <Flex gap="0.5rem" wrap="wrap">
        {movie.release_date && <Text><strong title={movie.release_date}>{movie.release_date.substring(0, 4)}</strong></Text>}
        {movie.runtime && <Text>{secondsToHourMin(movie.runtime)}</Text>}
        {movie.language && <Text>{langCodeToLang(movie.language)}</Text>}
        {movie.rating && <Text title="IMDb rating">{movie.rating} <StarIcon boxSize={2} /></Text>}
    </Flex>
}

function Plot({ movie }: { movie: IMovie }) {
    const [expand, setExpand] = useState(false)
    if (!movie.plot)
        return
    return <Text cursor="pointer" noOfLines={expand ? null : 3} onClick={() => {
        setExpand(!expand)
    }}>
        {movie.plot}
    </Text>
}

function Title({ movie }: { movie: IMovie }) {
    return <Box marginTop="-7px">
        <Heading as="h1">{movie.title || '<Missing title>'}</Heading>
        {movie.original_title != movie.title &&
            <Heading as="h2" fontSize="1.5rem" color="RGBA(255, 255, 255, 0.36)">{movie.original_title}</Heading>}

        {movie.tagline && <Text><i>{movie.tagline}</i></Text>}
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
    if (!movie.externals.imdb && !movie.externals.themoviedb)
        return
    return <Flex gap="0.5rem">
        {movie.externals.imdb && <Link href={`https://imdb.com/title/${movie.externals.imdb}`} isExternal>IMDb</Link>}
        {movie.externals.themoviedb && <Link href={`https://www.themoviedb.org/movie/${movie.externals.themoviedb}`} isExternal>TheMovieDB</Link>}
    </Flex>
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