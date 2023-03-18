import { StarIcon } from '@chakra-ui/icons'
import { Text, Box, Button, Heading, Link, Modal, ModalBody, ModalCloseButton, ModalContent, ModalHeader, ModalOverlay, Tag, useDisclosure, Stack, Wrap, WrapItem, Flex } from '@chakra-ui/react'
import { IMovie } from '@seplis/interfaces/movie'
import { Poster } from '../poster'
import { langCodeToLang, secondsToHourMin } from '../../utils'
import WatchlistButton from './watchlist-button'
import { IGenre } from '@seplis/interfaces/genre'
import { FaCog } from 'react-icons/fa'
import { MovieUpdate } from './settings'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { useEffect, useState } from 'react'
import { focusedBorder } from '@seplis/styles'
import PlayButton from './play-button'
import { MovieWatchedButton } from './watched-button'
import api from '@seplis/api'
import { useQuery } from '@tanstack/react-query'
import { MovieSkeleton } from './skeleton'
import ChromecastControls from '../player/chromecast-controls'
import MovieCollection from './collection'
import FavoriteButton from './favorite-button'


export function MovieLoad({ movieId, onLoaded }: { movieId: number, onLoaded?: (movie: IMovie) => void }) {
    const { isInitialLoading, data } = useQuery<IMovie>(['movie', movieId], async () => {
        const data = await api.get<IMovie>(`/2/movies/${movieId}`)
        if (onLoaded) onLoaded(data.data)
        return data.data
    })

    if (isInitialLoading)
        return <MovieSkeleton />

    if (!data?.title)
        return <SeriesWaitingForData movie={data} />

    return <Movie movie={data} />
}


export default function Movie({ movie }: { movie: IMovie }) {
    const { ref, focusKey, setFocus } = useFocusable()

    useEffect(() => {
        setFocus('MOVIE_PLAY')
    }, [])

    return <FocusContext.Provider value={focusKey}>
        <Stack direction="column" spacing="1rem" maxWidth="1100px">
            <Stack direction="row" spacing="1rem">
                <MoviePoster movie={movie} />
                <Stack direction="column" spacing="0.35rem" maxWidth="800px" ref={ref}>
                    <Title movie={movie} />
                    <BaseInfo movie={movie} />
                    <Genres genres={movie.genres} />
                    <ListButtons movie={movie} />
                    <Plot movie={movie} />
                    <ExternalLinks movie={movie} />
                    <WatchButtons movie={movie} />
                </Stack>
            </Stack>
            <ChromecastControls />
            {movie.collection && <MovieCollection collection={movie.collection} />}
        </Stack>
    </FocusContext.Provider>
}


function SeriesWaitingForData({ movie }: { movie: IMovie }) {
    return <Flex direction="column" align="center" gap="1rem">
        <Heading>Movie hasn't been updated, waiting for data</Heading>
        <Heading>Refresh to update</Heading>
        <DisplaySettings movie={movie} />
    </Flex>
}


function ListButtons({ movie }: { movie: IMovie }) {
    return <Flex gap="0.5rem" padding="0.25rem 0">
       <WatchlistButton movieId={movie.id} />
       <FavoriteButton movieId={movie.id} />
       <DisplaySettings movie={movie} />
    </Flex>
}


function WatchButtons({ movie }: { movie: IMovie }) {
    return <Flex gap="0.5rem" padding="0.25rem 0">
        <PlayButton movieId={movie.id} />
        <MovieWatchedButton movieId={movie.id} />
    </Flex>
}


function Genres({ genres }: { genres: IGenre[] }) {
    if (!genres || (genres.length < 0))
        return null

    return <Wrap padding="0.25rem 0">
        {genres.map(genre => (
            <WrapItem key={genre.id}><Genre genre={genre} /></WrapItem>
        ))}
    </Wrap>
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
    return <Wrap spacingX="0.75rem" lineHeight="1.3">
        {movie.release_date ? <WrapItem><strong title={movie.release_date}>{movie.release_date.substring(0, 4)}</strong></WrapItem> : null}
        {movie.language ? <WrapItem>{langCodeToLang(movie.language)}</WrapItem> : null}
        {movie.runtime ? <WrapItem>{secondsToHourMin(movie.runtime)}</WrapItem> : null}
        {movie.rating ? <WrapItem title="IMDb rating"><StarIcon mr="0.2rem" boxSize={3} color="yellow.400" mt="4px" />{movie.rating} IMDb</WrapItem> : null}
    </Wrap>
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
    return <Box marginTop="-7px" lineHeight="1.3">
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
    return <Wrap>
        {movie.externals.imdb && <WrapItem><Link href={`https://imdb.com/title/${movie.externals.imdb}`} isExternal>IMDb</Link></WrapItem>}
        {movie.externals.themoviedb && <WrapItem><Link href={`https://www.themoviedb.org/movie/${movie.externals.themoviedb}`} isExternal>TMDb</Link></WrapItem>}
    </Wrap>
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
                <ModalHeader>Settings</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <Box marginBottom="1rem">
                        <MovieUpdate movie={movie} />
                    </Box>
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}