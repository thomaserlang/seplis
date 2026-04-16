import { IImage } from '@/types/image.types'
import classes from './poster-image.module.css'

const GRADIENTS = [
    ['#1a1520', '#2a1f2e'],
    ['#0f1a1f', '#162028'],
    ['#1a1018', '#221520'],
    ['#0f1a14', '#162018'],
    ['#12101a', '#1c1828'],
    ['#0f1a1e', '#152025'],
    ['#150f1a', '#201528'],
    ['#1a0f0f', '#281515'],
]

function gradientFromTitle(title?: string | null) {
    if (!title) return GRADIENTS[0]
    let hash = 0
    for (let i = 0; i < title.length; i++) {
        hash = (hash * 31 + title.charCodeAt(i)) >>> 0
    }
    return GRADIENTS[hash % GRADIENTS.length]
}

interface Props {
    posterImage?: IImage | null
    title?: string | null
    sizeX?: number
}

export function PosterImage({ posterImage, title, sizeX = 320 }: Props) {
    return (
        <div className={classes.root}>
            {posterImage ? (
                <img
                    src={`${posterImage.url}@SX${sizeX}.webp`}
                    alt={title ?? undefined}
                    loading="lazy"
                />
            ) : (
                <div
                    className={classes.placeholder}
                    style={{
                        background: `linear-gradient(160deg, ${gradientFromTitle(title).join(', ')})`,
                    }}
                >
                    {title && (
                        <span className={classes.placeholderTitle}>
                            {title}
                        </span>
                    )}
                </div>
            )}
        </div>
    )
}
