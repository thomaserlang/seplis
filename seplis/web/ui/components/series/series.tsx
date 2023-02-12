import { StarIcon } from '@chakra-ui/icons'
import { Box, Button, Flex, Heading, Link, Modal, ModalBody, ModalCloseButton, ModalContent, ModalHeader, ModalOverlay, Tag, Text, useDisclosure } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { IGenre } from '@seplis/interfaces/genre'
import { ISeries } from '@seplis/interfaces/series'
import { focusedBorder } from '@seplis/styles'
import { langCodeToLang, secondsToHourMin } from '@seplis/utils'
import { useEffect } from 'react'
import { FaCog } from 'react-icons/fa'
import { Poster } from '../poster'
import Episodes from './episodes'
import FollowingButton from './following-button'
import Settings from './settings'

export default function Series({ series }: { series: ISeries }) {
    const { ref, focusKey, setFocus } = useFocusable()

    useEffect(() => {
        setFocus('SERIES_PLAY')
    }, [])

    return <FocusContext.Provider value={focusKey}>
        <Flex direction="column" gap="1rem" maxWidth="1075px">
            <Flex gap="1rem">
                <SeriesPoster series={series} />
                <Flex gap="0.5rem" direction="column" maxWidth="800px" ref={ref}>
                    <Title series={series} />
                    <BaseInfo series={series} />
                    <Genres genres={series.genres} />
                    <Buttons series={series} />
                    <Plot series={series} />
                    <ExternalLinks series={series} />
                </Flex>
            </Flex>
            <Episodes series={ series } />
        </Flex>
    </FocusContext.Provider>
}

function SeriesPoster({ series: series }: { series: ISeries }) {
    return <div className="poster-container-sizing">
        <div className="poster-container" style={{ 'flexShrink': '0' }}>
            <Poster url={`${series.poster_image?.url}@SX320.webp`} title={series.title} />
        </div>
    </div>
}

function Title({ series }: { series: ISeries }) {
    return <Box marginTop="-7px">
        <Heading as="h1">{series.title || '<Missing title>'}</Heading>
        {series.original_title != series.title &&
            <Heading as="h2" fontSize="1.5rem" color="RGBA(255, 255, 255, 0.36)">{series.original_title}</Heading>}

        {series.tagline && <Text><i>{series.tagline}</i></Text>}
    </Box>
}

function Plot({ series }: { series: ISeries }) {
    if (!series.plot)
        return
    return <Box>
        <Text><strong>Plot</strong></Text>
        <Text>{series.plot}</Text>
    </Box>
}

function BaseInfo({ series }: { series: ISeries }) {
    return <Flex gap="0.5rem" wrap="wrap">
        {series.premiered && <Text><strong title={series.premiered}>{series.premiered.substring(0, 4)}</strong></Text>}
        {series.runtime && <Text>{secondsToHourMin(series.runtime)}</Text>}
        {series.language && <Text>{langCodeToLang(series.language)}</Text>}
        {series.rating && <Text title="IMDb rating">{series.rating} <StarIcon boxSize={2} /></Text>}
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

function Buttons({ series }: { series: ISeries }) {
    return <Flex gap="0.5rem" wrap="wrap" padding="0.25rem 0">
        <FollowingButton seriesId={series.id} />
        <DisplaySettings series={series} />
    </Flex>
}

function ExternalLinks({ series }: { series: ISeries }) {
    if (!series.externals.imdb && !series.externals.themoviedb)
        return
    return <Flex gap="0.5rem">
        {series.externals.imdb && <Link href={`https://imdb.com/title/${series.externals.imdb}`} isExternal>IMDb</Link>}
        {series.externals.themoviedb && <Link href={`https://www.themoviedb.org/movie/${series.externals.themoviedb}`} isExternal>TheMovieDB</Link>}
    </Flex>
}


function DisplaySettings({ series }: { series: ISeries }) {
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
                <ModalHeader>{series.title} - Settings</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <Box marginBottom="1rem">
                        <Settings series={series} />
                    </Box>
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}