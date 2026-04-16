import React, { useState } from 'react'
import { SeriesSeason } from '../types/series-season.types'
import { EpisodeRangeWatchedModal } from './episode-range-watched-modal'

interface Props {
    children: React.ReactElement<{ onClick?: () => void }>
    seriesId: number
    season: number
    seasons: SeriesSeason[]
}

export function EpisodeRangeWatchedTrigger({
    children,
    seriesId,
    season,
    seasons,
}: Props) {
    const [opened, setOpened] = useState(false)

    return (
        <>
            {React.cloneElement(children, {
                onClick: () => {
                    children.props.onClick?.()
                    setOpened(true)
                },
            })}

            <EpisodeRangeWatchedModal
                opened={opened}
                onClose={() => setOpened(false)}
                seriesId={seriesId}
                season={season}
                seasons={seasons}
            />
        </>
    )
}
