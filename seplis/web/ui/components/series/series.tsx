import { StarIcon } from '@chakra-ui/icons'
import { Box, Button, Flex, Heading, Link, Modal, ModalBody, ModalCloseButton, ModalContent, ModalHeader, ModalOverlay, Stack, Tag, Text, useDisclosure, Wrap, WrapItem } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import api from '@seplis/api'
import { IGenre } from '@seplis/interfaces/genre'
import { ISeries, ISeriesSeason } from '@seplis/interfaces/series'
import { focusedBorder } from '@seplis/styles'
import { isAuthed, langCodeToLang, secondsToHourMin } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { FaCog } from 'react-icons/fa'
import ChromecastControls from '../player/chromecast-controls'
import { Poster } from '../poster'
import EpisodeLastWatched from './episode-last-watched'
import EpisodeNextToAir from './episode-next-to-air'
import EpisodeToWatch from './episode-to-watch'
import Episodes from './episodes'
import WatchlistButton from './watchlist-button'
import { SeriesUpdate } from './settings'
import SeriesSkeleton from './skeleton'
import FavoriteButton from './favorite-button'


export function SeriesLoad({ seriesId, onLoaded }: { seriesId: number, onLoaded?: (movie: ISeries) => void }) {
    const { isInitialLoading, data } = useQuery<ISeries>(['series', seriesId], async () => {
        const data = await api.get<ISeries>(`/2/series/${seriesId}`)
        if (onLoaded) onLoaded(data.data)
        return data.data
    })

    if (isInitialLoading)
        return <SeriesSkeleton />

    if (!data?.title)
        return <SeriesWaitingForData series={data} />

    return <Series series={data} />
}


export default function Series({ series }: { series: ISeries }) {
    const { ref, focusKey, setFocus } = useFocusable()

    useEffect(() => {
        setFocus('SERIES_PLAY')
    }, [])

    return <FocusContext.Provider value={focusKey}>
        <Stack direction="column" spacing="1rem" maxWidth="1100px">
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

            <ChromecastControls />

            <UserEpisodes series={series} />

            <SeasonEpisodes series={series} />

        </Stack>
    </FocusContext.Provider>
}


function SeriesWaitingForData({ series }: { series: ISeries }) {
    return <Flex direction="column" align="center" gap="1rem">
        <Heading>Series hasn't been updated, waiting for data</Heading>
        <Heading>Refresh to update</Heading>
        <DisplaySettings series={series} />
    </Flex>
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
        {series.runtime ? <WrapItem>{secondsToHourMin(series.runtime)}</WrapItem> : null}
        <SeasonsText seasons={series.seasons} />
        <EpisodesText seasons={series.seasons} />
        {series.rating ? <WrapItem title="IMDb rating"><StarIcon mr="0.2rem" boxSize={3} color="yellow.400" mt="4px" />{series.rating} IMDb</WrapItem> : null}
    </Wrap>
}


function SeasonsText({ seasons }: { seasons: ISeriesSeason[] }) {
    return <>
        {seasons?.length > 0 && <Text>{seasons.length} {seasons.length == 1 ? 'season' : 'seasons'}</Text>}
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


function Buttons({ series }: { series: ISeries }) {
    return <Wrap padding="0.25rem 0">
        <WrapItem><WatchlistButton seriesId={series.id} /></WrapItem>
        <WrapItem><FavoriteButton seriesId={series.id} /></WrapItem>
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
            {series.externals.themoviedb && <Link href={`https://www.themoviedb.org/tv/${series.externals.themoviedb}`} isExternal>TMDb</Link>}
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
                <ModalHeader>Settings</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <Box marginBottom="1rem">
                        <SeriesUpdate series={series} />
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
    return <Flex gap="0.5rem" align="stretch" wrap="wrap">
        <EpisodeLastWatched seriesId={series.id} />
        <EpisodeToWatch seriesId={series.id} />
    </Flex>
}


function SeasonEpisodes({ series }: { series: ISeries }) {
    return <>
        {series.seasons.length > 0 && <Stack>
            <Heading fontSize="2xl" fontWeight="600">Episodes</Heading>
            <Episodes series={series} defaultSeason={series.seasons[series.seasons.length - 1].season} />
        </Stack>}
    </>
}