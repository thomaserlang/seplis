import { StarIcon } from '@chakra-ui/icons'
import { Box, Button, Flex, Heading, Link, Modal, ModalBody, ModalCloseButton, ModalContent, ModalHeader, ModalOverlay, Stack, Tag, Text, useDisclosure, Wrap, WrapItem } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { IGenre } from '@seplis/interfaces/genre'
import { ISeries, ISeriesSeason } from '@seplis/interfaces/series'
import { focusedBorder } from '@seplis/styles'
import { isAuthed, langCodeToLang, secondsToHourMin } from '@seplis/utils'
import { useEffect, useState } from 'react'
import { FaCog } from 'react-icons/fa'
import { Poster } from '../poster'
import EpisodeLastWatched from './episode-last-watched'
import EpisodeNextToAir from './episode-next-to-air'
import EpisodeToWatch from './episode-to-watch'
import Episodes from './episodes'
import FollowingButton from './following-button'
import Settings from './settings'


export default function Series({ series }: { series: ISeries }) {
    const { ref, focusKey, setFocus } = useFocusable()

    useEffect(() => {
        setFocus('SERIES_PLAY')
    }, [])

    return <FocusContext.Provider value={focusKey}>
        <Stack direction="column" spacing="1rem" maxWidth="1075px">
            <Stack spacing="1rem" direction="row" >
                <SeriesPoster series={series} />
                <Stack spacing="0.5rem" direction="column" maxWidth="800px" ref={ref}>
                    <Title series={series} />
                    <BaseInfo series={series} />
                    <Genres genres={series.genres} />
                    <Buttons series={series} />
                    <Plot series={series} />
                    <ExternalLinks series={series} />
                    <EpisodeNextToAir seriesId={series.id} />
                </Stack>
            </Stack>

            <UserEpisodes series={series} />

            <SeasonEpisodes series={series} />

        </Stack>
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
    return <Box marginTop="-7px" lineHeight="1.3">
        <Heading as="h1">{series.title || '<Missing title>'}</Heading>
        {series.original_title != series.title &&
            <Heading as="h2" fontSize="1.5rem" color="RGBA(255, 255, 255, 0.36)">{series.original_title}</Heading>}

        {series.tagline && <Text><i>{series.tagline}</i></Text>}
    </Box>
}


function Plot({ series }: { series: ISeries }) {
    const [expand, setExpand] = useState(false)
    if (!series.plot)
        return
    return <Text cursor="pointer" noOfLines={expand ? null : 3} onClick={() => {
        setExpand(!expand)
    }}>{series.plot}</Text>
}


function BaseInfo({ series }: { series: ISeries }) {
    return <Wrap spacingX="0.75rem" lineHeight="1.3">        
        {series.premiered && <WrapItem><strong title={series.premiered}>{series.premiered.substring(0, 4)}</strong></WrapItem>}
        {series.language && <WrapItem>{langCodeToLang(series.language)}</WrapItem>}
        {series.runtime && <WrapItem>{secondsToHourMin(series.runtime)}</WrapItem>}
        <SeasonsText seasons={series.seasons} />
        <EpisodesText seasons={series.seasons} />
        {series.rating && <WrapItem title="IMDb rating"><Flex alignItems="center">{series.rating} <StarIcon marginLeft="0.2rem" boxSize={3} /></Flex></WrapItem>}
    </Wrap>
}


function SeasonsText({ seasons }: { seasons: ISeriesSeason[] }) {
    return <>
        {seasons && <Text>{seasons.length} {seasons.length == 1 ? 'season' : 'seasons'}</Text>}
    </>
}

function EpisodesText({ seasons }: { seasons: ISeriesSeason[] }) {
    let episodes = 0
    if (seasons)
        for (const season of seasons) {
            episodes += season.total
        }
    return <>
        <Text>{episodes} {episodes == 1 ? 'episode' : 'episodes'}</Text>
    </>
}


function Genres({ genres }: { genres: IGenre[] }) {
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


function Buttons({ series }: { series: ISeries }) {
    return <Wrap padding="0.25rem 0">
        <WrapItem><FollowingButton seriesId={series.id} /></WrapItem>
        <WrapItem><DisplaySettings series={series} /></WrapItem>
    </Wrap>
}


function ExternalLinks({ series }: { series: ISeries }) {
    if (!series.externals.imdb && !series.externals.themoviedb)
        return
    return <Wrap>
        <WrapItem>
            {series.externals.imdb && <Link href={`https://imdb.com/title/${series.externals.imdb}`} isExternal>IMDb</Link>}
        </WrapItem>
        <WrapItem>
            {series.externals.themoviedb && <Link href={`https://www.themoviedb.org/movie/${series.externals.themoviedb}`} isExternal>TheMovieDB</Link>}
        </WrapItem>
    </Wrap>
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


function UserEpisodes({ series }: { series: ISeries }) {
    if (series.seasons.length == 0)
        return
    if (!isAuthed())
        return
    return <Wrap>
        <Flex grow="1"><WrapItem width="100%"><EpisodeToWatch seriesId={series.id} /></WrapItem></Flex>
        <Flex grow="1"><WrapItem width="100%"><EpisodeLastWatched seriesId={series.id} /></WrapItem></Flex>
    </Wrap>
}


function SeasonEpisodes({ series }: { series: ISeries }) {
    return <>
        {series.seasons.length > 0 && <Stack>
            <Heading fontSize="2xl" fontWeight="600">Episodes</Heading>
            <Episodes series={series} defaultSeason={series.seasons[series.seasons.length - 1].season} />
        </Stack>}
    </>
}