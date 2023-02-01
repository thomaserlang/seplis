import { StarIcon } from '@chakra-ui/icons';
import { Box, Flex, Heading, Tag } from '@chakra-ui/react';
import { IMovie } from '@seplis/interfaces/movie';
import { Poster } from '../poster';
import { langCodeToLang, secondsToHourMin } from '../../utils'
import StaredButton from './stared-button';
import { IGenre } from '@seplis/interfaces/genre';

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
                <Plot movie={movie} />
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
        <div>{movie.release_date && <strong>{movie.release_date.substring(0, 4)}</strong>}</div>
        <div>{secondsToHourMin(movie.runtime)}</div>
        <div>{langCodeToLang(movie.language)}</div>
        <div>{movie.rating} <StarIcon boxSize={2} /></div>
    </Flex>
}

function Plot({ movie }: { movie: IMovie }) {
    return <Flex direction="column" rowGap="0.5rem">
        <div><i>{movie.tagline}</i></div>

        <div>
            {movie.plot}
        </div>
    </Flex>
}

function Title({ movie }: { movie: IMovie }) {
    return <Flex direction="column" rowGap="0.5rem">
            <Flex columnGap="0.5rem" justifyContent="flex-start">
            <Heading>{movie.title || '<Missing title>'}</Heading>
            <Box marginLeft="auto"><StaredButton movieId={movie.id} /></Box>
        </Flex>

        {movie.original_title != movie.title && <Heading as="h2">movie.original_title</Heading>}
    </Flex>
}

function MoviePoster({ movie }: { movie: IMovie }) {
    return <div className="poster-container-sizing">
        <div className="poster-container" style={{'flexShrink': '0'}}>
            <Poster url={`${movie.poster_image?.url}@SX320.webp`} title={movie.title} />
        </div>
    </div>
}