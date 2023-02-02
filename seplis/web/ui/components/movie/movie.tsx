import { StarIcon } from '@chakra-ui/icons';
import { Box, Button, Flex, Heading, Icon, Link, Modal, ModalBody, ModalCloseButton, ModalContent, ModalHeader, ModalOverlay, Tag, useDisclosure } from '@chakra-ui/react';
import { IMovie } from '@seplis/interfaces/movie';
import { Poster } from '../poster';
import { langCodeToLang, secondsToHourMin } from '../../utils'
import StaredButton from './stared-button';
import { IGenre } from '@seplis/interfaces/genre';
import { FaCog, FaPlay } from 'react-icons/fa';
import Settings from './settings';

interface IProps {
    movie: IMovie
}

export default function Movie({ movie }: IProps) {

    return <Flex direction={"column"} rowGap="0.5rem">
        <Flex columnGap="1rem">
            <MoviePoster movie={movie} />

            <Flex direction="column" rowGap="0.5rem" maxWidth="800px">
                <Title movie={movie} />
                <BaseInfo movie={movie} />
                <Genres genres={movie.genres} />
                <Flex columnGap="0.5rem" marginTop="0.5rem" marginBottom="0.5rem">
                    <Button leftIcon={<Icon as={FaPlay} />}>Play</Button>
                    <StaredButton movieId={movie.id} />
                    <DisplaySettings movie={movie} />
                </Flex>
                <Plot movie={movie} />
                <ExternalLinks movie={movie} />
            </Flex>
        </Flex>
    </Flex>
}

function Genres({ genres }: { genres: IGenre[] }) {
    return <Flex columnGap="0.5rem" rowGap="0.5rem" direction="row" wrap="wrap">
        {genres.map(genre => (
            <Tag key={genre.id}>{genre.name}</Tag>
        ))}
    </Flex>
}

function BaseInfo({ movie }: { movie: IMovie }) {
    return <Flex columnGap="0.5rem" rowGap="0.5rem" direction="row" wrap="wrap">
        {movie.release_date && <div><strong title={movie.release_date}>{movie.release_date.substring(0, 4)}</strong></div>}
        {movie.runtime && <div>{secondsToHourMin(movie.runtime)}</div>}
        {movie.language && <div>{langCodeToLang(movie.language)}</div>}
        {movie.rating && <div title="IMDb rating">{movie.rating} <StarIcon boxSize={2} /></div>}
    </Flex>
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
        <div className="poster-container" style={{'flexShrink': '0'}}>
            <Poster url={`${movie.poster_image?.url}@SX320.webp`} title={movie.title} />
        </div>
    </div>
}

function ExternalLinks({ movie }: { movie: IMovie }) {
    if (!movie.externals.imdb || !movie.externals.themoviedb)
        return
    return <Flex columnGap="0.5rem">
        {movie.externals.imdb && <Link href={`https://imdb.com/title/${movie.externals.imdb}`} isExternal>IMDb</Link>}
        {movie.externals.themoviedb && <Link href={`https://www.themoviedb.org/movie/${movie.externals.themoviedb}`} isExternal>TheMovieDB</Link>}
    </Flex>
}

function DisplaySettings({ movie }: { movie: IMovie }) {
    const { isOpen, onOpen, onClose } = useDisclosure()

    return <>
        <Button onClick={onOpen} leftIcon={<FaCog />}>Settings</Button>

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