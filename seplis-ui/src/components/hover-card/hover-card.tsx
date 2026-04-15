import classes from './hover-card.module.css'

interface Props {
    rect: DOMRect
    containerRect: DOMRect
    isLeaving: boolean
    onMouseEnter: () => void
    onMouseLeave: () => void
    children: React.ReactNode
    minWidth?: number
}

export function HoverCard({
    rect,
    containerRect,
    isLeaving,
    onMouseEnter,
    onMouseLeave,
    children,
    minWidth = 270,
}: Props) {
    const hoverWidth = Math.max(rect.width * 1.6, minWidth)
    let left = rect.left - containerRect.left + rect.width / 2 - hoverWidth / 2
    left = Math.max(0, Math.min(left, containerRect.width - hoverWidth))

    const originX =
        ((rect.left - containerRect.left + rect.width / 2 - left) /
            hoverWidth) *
        100

    const style: React.CSSProperties = {
        left,
        width: `clamp(${minWidth}px, ${hoverWidth}px, 100%)`,
        top: rect.top - containerRect.top + rect.height / 2,
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
