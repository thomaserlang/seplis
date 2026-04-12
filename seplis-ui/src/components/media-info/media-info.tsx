import { Genre } from '@/types/genre.types'
import { Flex, Text, UnstyledButton } from '@mantine/core'
import { useEffect, useRef, useState } from 'react'
import { Genres } from '../genres'
import classes from './media-info.module.css'

export interface MediaInfoProps {
    posterUrl?: string
    accentHue?: number
    status?: MediaStatus
    title: string
    originalTitle?: string | null
    tagline?: string | null
    metaItems: MediaMetaItem[]
    genres: Genre[]
    plot?: string | null
    children: React.ReactNode
}

export function MediaInfo({
    posterUrl,
    accentHue = 250,
    status,
    title,
    originalTitle,
    tagline,
    metaItems,
    genres,
    plot,
    children,
}: MediaInfoProps) {
    return (
        <div
            className={classes.root}
            style={{ '--accent-hue': accentHue } as React.CSSProperties}
        >
            <div className={classes.posterPanel}>
                {posterUrl && (
                    <img src={posterUrl} className={classes.posterImg} />
                )}
                {status && (
                    <div className={classes.posterMeta}>
                        <Flex align="center" gap="0.4rem">
                            <span
                                className={classes.statusDot}
                                style={{ background: status.dot }}
                            />
                            <Text
                                size="xs"
                                fw={600}
                                style={{ color: 'oklch(1 0 0 / 0.7)' }}
                            >
                                {status.label}
                            </Text>
                        </Flex>
                    </div>
                )}
            </div>

            <div className={classes.infoPanel}>
                <div>
                    <Text fw={700} size="xl" lh={1.2}>
                        {title}
                    </Text>
                    {originalTitle && originalTitle !== title && (
                        <Text size="sm" c="dimmed" mt="0.2rem">
                            {originalTitle}
                        </Text>
                    )}
                    {tagline && (
                        <Text size="sm" c="dimmed" fs="italic" mt="0.25rem">
                            {tagline}
                        </Text>
                    )}
                </div>

                {metaItems.length > 0 && (
                    <>
                        <Flex gap="1.25rem" rowGap="0.6rem" wrap="wrap">
                            {metaItems.map((item) => (
                                <Flex
                                    key={item.label}
                                    direction="column"
                                    gap="0.1rem"
                                >
                                    <Text
                                        size="xs"
                                        c="dimmed"
                                        tt="uppercase"
                                        fw={600}
                                        lts="0.05em"
                                    >
                                        {item.label}
                                    </Text>
                                    <Text
                                        size="sm"
                                        fw={item.color ? 700 : 600}
                                        style={
                                            item.color
                                                ? { color: item.color }
                                                : undefined
                                        }
                                    >
                                        {item.value}
                                    </Text>
                                </Flex>
                            ))}
                        </Flex>
                    </>
                )}

                <Genres genres={genres} size="sm" />

                {plot && <PlotText plot={plot} />}

                {children}
            </div>
        </div>
    )
}

export interface MediaStatus {
    label: string
    dot: string
}

export interface MediaMetaItem {
    label: string
    value: string
    color?: string
}

export interface MediaStatItem {
    label: string
    value: string
}

function PlotText({ plot }: { plot: string }) {
    const [expanded, setExpanded] = useState(false)
    const [overflows, setOverflows] = useState(false)
    const textRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const el = textRef.current
        if (el) {
            setOverflows(el.scrollHeight > el.clientHeight)
        }
    }, [plot])

    return (
        <UnstyledButton
            onClick={
                overflows || expanded ? () => setExpanded((e) => !e) : undefined
            }
            style={{
                cursor: overflows || expanded ? 'pointer' : 'default',
            }}
        >
            <Text
                ref={textRef}
                size="sm"
                c="dimmed"
                lineClamp={expanded ? undefined : 3}
            >
                {plot}
            </Text>
        </UnstyledButton>
    )
}
