import { CastMember } from '@/types/person.types'
import { PosterImage } from '../poster-image'
import classes from './cast-member-card.module.css'

interface Props {
    castMember: CastMember
    showTotalEpisodes?: boolean
}

function initials(name: string) {
    return name
        .split(' ')
        .filter(Boolean)
        .slice(0, 2)
        .map((w) => w[0].toUpperCase())
        .join('')
}

export function CastMemberCard({ castMember, showTotalEpisodes }: Props) {
    const { person, roles, character } = castMember
    const characterDisplay =
        roles && roles.length > 0
            ? roles.map((r) => r.character).join(' / ')
            : character

    return (
        <div className={classes.card}>
            <div className={classes.imageWrap}>
                <PosterImage
                    posterImage={castMember.person.profile_image}
                    title={initials(castMember.person.name)}
                />
            </div>
            <div className={classes.info}>
                <span className={classes.name}>{person.name}</span>
                {characterDisplay && (
                    <span className={classes.character}>
                        {characterDisplay}
                    </span>
                )}
                {showTotalEpisodes &&
                    castMember.total_episodes !== undefined && (
                        <span className={classes.character}>
                            {castMember.total_episodes} episodes
                        </span>
                    )}
            </div>
        </div>
    )
}
