import classes from './hover-card.module.css'

interface Props {
    rect: DOMRect
    isLeaving: boolean
    onMouseEnter: () => void
    onMouseLeave: () => void
    children: React.ReactNode
}

export function HoverCard({
    rect,
    isLeaving,
    onMouseEnter,
    onMouseLeave,
    children,
}: Props) {
    const hoverWidth = rect.width * 1.6
    const margin = 8
    let left = rect.left + rect.width / 2 - hoverWidth / 2
    left = Math.max(margin, Math.min(left, window.innerWidth - hoverWidth - margin))

    const originX = ((rect.left + rect.width / 2 - left) / hoverWidth) * 100

    const style: React.CSSProperties = {
        left,
        width: `clamp(16.875rem, ${hoverWidth}px, 100%)`,
        top: rect.top + rect.height / 2,
        transformOrigin: `${originX}% 50%`,
    }

    return (
        <div
            className={`${classes.hoverCard} ${isLeaving ? classes.hoverCardLeaving : ''}`}
            style={style}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
        >
            {children}
        </div>
    )
}
