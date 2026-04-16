import { Logo } from '@/components/logo'
import { PosterImage } from '@/components/poster-image/poster-image'
import { MoviesSlider, useGetMovies } from '@/features/movie'
import { SeriesSlider, useGetSeriesList } from '@/features/series'
import { IImage } from '@/types/image.types'
import { pageItemsFlatten } from '@/utils/api-crud'
import {
    Button,
    Container,
    Group,
    SimpleGrid,
    Stack,
    Text,
    ThemeIcon,
    Title,
} from '@mantine/core'
import {
    ArrowRightIcon,
    CheckCircleIcon,
    DevicesIcon,
    UsersThreeIcon,
} from '@phosphor-icons/react'
import { Link, useNavigate } from 'react-router-dom'
import classes from './landing-view.module.css'

type PreviewItem = {
    id: number
    poster_image: IImage | null
    title: string | null
}

const features = [
    {
        icon: CheckCircleIcon,
        title: 'Track watched status',
        description:
            'Keep movies, episodes, and upcoming picks organized in one place.',
        illustration: <LibraryIllustration />,
    },
    {
        icon: DevicesIcon,
        title: 'Connect your own play server',
        description:
            'Use your existing server setup for playback without changing how you host media.',
        illustration: <ServerIllustration />,
    },
    {
        icon: UsersThreeIcon,
        title: 'Share access',
        description:
            'Invite family and friends, or join other shared libraries from the same account.',
        illustration: <SharingIllustration />,
    },
]

export function LandingView() {
    const navigate = useNavigate()

    return (
        <Container size="xl" className={classes.page}>
            <section className={classes.hero}>
                <div className={classes.heroInner}>
                    <Stack gap="lg" className={classes.copy}>
                        <Group gap="lg">
                            <Logo size="3.25rem" />
                            <Text className={classes.eyebrow}>SEPLIS</Text>
                        </Group>

                        <div>
                            <Title order={1} className={classes.title}>
                                Keep track of what you have watched and what to
                                watch next
                            </Title>
                            <Text className={classes.description}>
                                SEPLIS is a media tracking app for personal
                                libraries. Keep a watch history, maintain a
                                watchlist, connect your own play server, and
                                share access with friends and family from one
                                place.
                            </Text>
                        </div>

                        <Group gap="sm">
                            <Button
                                component={Link}
                                to="/signup"
                                size="md"
                                radius="sm"
                                rightSection={<ArrowRightIcon size={16} />}
                            >
                                Create account
                            </Button>
                            <Button
                                component={Link}
                                to="/login"
                                size="md"
                                radius="sm"
                                variant="default"
                            >
                                Log in
                            </Button>
                        </Group>

                        <div className={classes.metaRow}>
                            <Text className={classes.metaItem}>
                                Watched history
                            </Text>
                            <Text className={classes.metaItem}>Watchlist</Text>
                            <Text className={classes.metaItem}>
                                Server sharing
                            </Text>
                        </div>
                    </Stack>

                    <div className={classes.heroArt}>
                        <LandingContentPreview />
                    </div>
                </div>
            </section>

            <section className={classes.popularSection}>
                <div className={classes.popularSliders}>
                    <SeriesSlider
                        title="Popular series"
                        onClick={() => navigate('/login')}
                        params={{
                            sort: ['popularity_desc'],
                        }}
                    />
                    <MoviesSlider
                        title="Popular movies"
                        onClick={() => navigate('/login')}
                        params={{
                            sort: ['popularity_desc'],
                        }}
                    />
                </div>
            </section>

            <section className={classes.section}>
                <div className={classes.sectionHeader}>
                    <Text className={classes.sectionEyebrow}>How it works</Text>
                    <Title order={2} className={classes.sectionTitle}>
                        Built for private libraries and shared households.
                    </Title>
                    <Text className={classes.sectionDescription}>
                        The front page is intentionally simple: track progress,
                        decide what to watch next, and play from infrastructure
                        you already control.
                    </Text>
                </div>

                <SimpleGrid cols={{ base: 1, md: 3 }} spacing="xl">
                    {features.map((feature) => (
                        <article
                            key={feature.title}
                            className={classes.feature}
                        >
                            <div className={classes.featureIllustration}>
                                {feature.illustration}
                            </div>
                            <Group gap="sm" mb="sm">
                                <ThemeIcon
                                    size={34}
                                    radius="sm"
                                    className={classes.featureIcon}
                                >
                                    <feature.icon size={18} weight="fill" />
                                </ThemeIcon>
                                <Title
                                    order={3}
                                    className={classes.featureTitle}
                                >
                                    {feature.title}
                                </Title>
                            </Group>
                            <Text className={classes.featureDescription}>
                                {feature.description}
                            </Text>
                        </article>
                    ))}
                </SimpleGrid>
            </section>
        </Container>
    )
}

function LandingContentPreview() {
    const { data: seriesData } = useGetSeriesList({
        params: {
            per_page: 1,
            sort: ['popularity_desc'],
        },
    })
    const { data: moviesData } = useGetMovies({
        params: {
            per_page: 1,
            sort: ['popularity_desc'],
        },
    })

    const series = pageItemsFlatten(seriesData)
        .map(toPreviewItem)
        .filter(isPreviewItem)
        .slice(0, 6)
    const movies = pageItemsFlatten(moviesData)
        .map(toPreviewItem)
        .filter(isPreviewItem)
        .slice(0, 6)
    const featured = movies[0] || series[0]

    return (
        <div className={classes.previewFeature}>
            <div className={classes.previewPlayer}>
                {featured ? (
                    <PosterImage
                        posterImage={featured.poster_image}
                        title={featured.title}
                    />
                ) : (
                    <div className={classes.previewFallback} />
                )}
            </div>

            <div className={classes.previewInfo}>
                <div className={classes.previewInfoLineLg} />
                <div className={classes.previewInfoLine} />
                <div className={classes.previewInfoLineShort} />
                <div className={classes.previewStats}>
                    <span className={classes.previewStatPill}>watched 12x</span>
                    <span className={classes.previewStatPillMuted}>
                        on watchlist
                    </span>
                </div>
            </div>
        </div>
    )
}

function toPreviewItem(
    item:
        | {
              id: number
              poster_image: IImage | null
              title: string | null
          }
        | null
        | undefined,
): PreviewItem | null {
    if (!item) return null
    return {
        id: item.id,
        poster_image: item.poster_image,
        title: item.title,
    }
}

function isPreviewItem(item: PreviewItem | null): item is PreviewItem {
    return item !== null
}

function LibraryIllustration() {
    return (
        <svg
            viewBox="0 0 320 190"
            className={classes.illustration}
            aria-hidden="true"
        >
            <rect
                x="24"
                y="30"
                width="272"
                height="132"
                rx="16"
                fill="var(--card)"
                stroke="var(--border-color)"
            />
            <rect
                x="46"
                y="52"
                width="56"
                height="78"
                rx="8"
                fill="color-mix(in oklab, var(--foreground) 10%, var(--card))"
            />
            <rect
                x="118"
                y="58"
                width="102"
                height="10"
                rx="5"
                fill="var(--foreground)"
            />
            <rect
                x="118"
                y="80"
                width="136"
                height="8"
                rx="4"
                fill="var(--muted-foreground)"
            />
            <rect
                x="118"
                y="98"
                width="116"
                height="8"
                rx="4"
                fill="var(--muted-foreground)"
            />
            <rect
                x="118"
                y="118"
                width="64"
                height="16"
                rx="8"
                fill="color-mix(in oklab, var(--foreground) 14%, var(--card))"
            />
            <path
                d="M241 118 L250 127 L268 108"
                fill="none"
                stroke="var(--foreground)"
                strokeWidth="7"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
        </svg>
    )
}

function ServerIllustration() {
    return (
        <svg
            viewBox="0 0 320 190"
            className={classes.illustration}
            aria-hidden="true"
        >
            <rect
                x="58"
                y="32"
                width="92"
                height="126"
                rx="12"
                fill="var(--card)"
                stroke="var(--border-color)"
            />
            <rect
                x="170"
                y="32"
                width="92"
                height="126"
                rx="12"
                fill="var(--card)"
                stroke="var(--border-color)"
            />
            {[58, 82, 106].map((y) => (
                <g key={y}>
                    <rect
                        x="76"
                        y={y}
                        width="56"
                        height="10"
                        rx="5"
                        fill="var(--muted-foreground)"
                    />
                    <circle
                        cx="118"
                        cy={y + 5}
                        r="5"
                        fill="var(--foreground)"
                    />
                </g>
            ))}
            {[58, 82, 106].map((y) => (
                <g key={`r-${y}`}>
                    <rect
                        x="188"
                        y={y}
                        width="56"
                        height="10"
                        rx="5"
                        fill="var(--muted-foreground)"
                    />
                    <circle
                        cx="230"
                        cy={y + 5}
                        r="5"
                        fill="var(--foreground)"
                    />
                </g>
            ))}
            <path
                d="M150 96 C165 96, 165 96, 170 96"
                fill="none"
                stroke="var(--foreground)"
                strokeWidth="6"
                strokeLinecap="round"
            />
        </svg>
    )
}

function SharingIllustration() {
    return (
        <svg
            viewBox="0 0 320 190"
            className={classes.illustration}
            aria-hidden="true"
        >
            <circle
                cx="92"
                cy="70"
                r="24"
                fill="color-mix(in oklab, var(--foreground) 10%, var(--card))"
                stroke="var(--border-color)"
            />
            <circle
                cx="160"
                cy="56"
                r="24"
                fill="color-mix(in oklab, var(--foreground) 12%, var(--card))"
                stroke="var(--border-color)"
            />
            <circle
                cx="228"
                cy="70"
                r="24"
                fill="color-mix(in oklab, var(--foreground) 10%, var(--card))"
                stroke="var(--border-color)"
            />
            <path
                d="M92 120 C92 103, 114 96, 132 96 C150 96, 160 106, 160 120"
                fill="none"
                stroke="var(--foreground)"
                strokeWidth="8"
                strokeLinecap="round"
            />
            <path
                d="M160 106 C160 90, 180 84, 196 84 C212 84, 228 92, 228 106"
                fill="none"
                stroke="var(--foreground)"
                strokeWidth="8"
                strokeLinecap="round"
            />
            <rect
                x="66"
                y="132"
                width="188"
                height="28"
                rx="14"
                fill="var(--card)"
                stroke="var(--border-color)"
            />
            <circle cx="92" cy="146" r="6" fill="var(--foreground)" />
            <rect
                x="108"
                y="141"
                width="64"
                height="10"
                rx="5"
                fill="var(--muted-foreground)"
            />
            <rect
                x="186"
                y="137"
                width="50"
                height="18"
                rx="9"
                fill="color-mix(in oklab, var(--foreground) 14%, var(--card))"
            />
        </svg>
    )
}
