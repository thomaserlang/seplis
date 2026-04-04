import { MediaInfo, MediaMetaItem, MediaStatus } from '@/components/media-info'
import { langCodeToLang } from '@/utils/language.utils'
import { Flex } from '@mantine/core'
import { Movie } from '../types/movie.types'
import { MovieFavoriteButton } from './movie-favorite-button'
import { MovieWatchedButton } from './movie-watched-button'
import { MovieWatchlistButton } from './movie-watchlist-button'

interface Props {
    movie: Movie
}

const STATUS: Record<number, MediaStatus> = {
    0: { label: 'Unknown', dot: 'oklch(0.6 0 0)' },
    1: { label: 'Released', dot: 'oklch(0.7 0.17 175)' },
    2: { label: 'In production', dot: 'oklch(0.6 0.2 250)' },
    3: { label: 'Planned', dot: 'oklch(0.55 0.22 295)' },
    4: { label: 'Cancelled', dot: 'oklch(0.7 0.18 55)' },
    5: { label: 'Rumored', dot: 'oklch(0.6 0 0)' },
}

function formatRuntime(minutes: number) {
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    if (h === 0) return `${m}m`
    if (m === 0) return `${h}h`
    return `${h}h ${m}m`
}

function formatMoney(amount: number) {
    if (amount >= 1_000_000_000)
        return `$${(amount / 1_000_000_000).toFixed(1)}B`
    if (amount >= 1_000_000) return `$${(amount / 1_000_000).toFixed(0)}M`
    return `$${amount.toLocaleString()}`
}

export function MovieInfo({ movie }: Props) {
    const metaItems: MediaMetaItem[] = [
        movie.release_date
            ? { label: 'Year', value: movie.release_date.substring(0, 4) }
            : null,
        movie.runtime
            ? { label: 'Runtime', value: formatRuntime(movie.runtime) }
            : null,
        movie.language
            ? { label: 'Language', value: langCodeToLang(movie.language) }
            : null,
        movie.rating != null
            ? {
                  label: 'IMDb',
                  value: `★ ${movie.rating.toFixed(1)}`,
                  color: 'oklch(0.82 0.18 85)',
              }
            : null,
        movie.budget
            ? { label: 'Budget', value: formatMoney(movie.budget) }
            : null,
        movie.revenue
            ? { label: 'Revenue', value: formatMoney(movie.revenue) }
            : null,
    ].filter(Boolean) as MediaMetaItem[]

    return (
        <MediaInfo
            posterUrl={
                movie.poster_image
                    ? `${movie.poster_image.url}@SX320.webp`
                    : undefined
            }
            accentHue={30}
            status={movie.status != null ? STATUS[movie.status] : undefined}
            title={movie.title || movie.original_title || 'Unknown title'}
            originalTitle={movie.original_title}
            tagline={movie.tagline}
            metaItems={metaItems}
            genres={movie.genres}
            plot={movie.plot}
            renderMainButtons={() => (
                <Flex gap="0.5rem" wrap="wrap">
                    <MovieWatchlistButton movieId={movie.id} />
                    <MovieFavoriteButton movieId={movie.id} />
                    <MovieWatchedButton movieId={movie.id} />
                </Flex>
            )}
        />
    )
}
