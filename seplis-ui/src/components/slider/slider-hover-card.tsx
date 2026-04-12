import classes from './slider.module.css'

interface Props {
    rect: DOMRect
    showAbove: boolean
    isLeaving: boolean
    onMouseEnter: () => void
    onMouseLeave: () => void
    children: React.ReactNode
}

export function SliderHoverCard({
    rect,
    showAbove,
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
        width: hoverWidth,
        transformOrigin: `${originX}% ${showAbove ? 'bottom' : 'top'}`,
        ...(showAbove
            ? { bottom: window.innerHeight - rect.top + 4 }
            : { top: rect.top }),
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
