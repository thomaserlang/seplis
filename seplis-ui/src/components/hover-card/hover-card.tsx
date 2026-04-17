import { useLayoutEffect, useRef, useState } from 'react'
import classes from './hover-card.module.css'

interface Props {
    rect: DOMRect
    containerRect: DOMRect
    viewportRect: DOMRect
    isLeaving: boolean
    onMouseEnter: () => void
    onMouseLeave: () => void
    children: React.ReactNode
    minWidth?: number
}

export function HoverCard({
    rect,
    containerRect,
    viewportRect,
    isLeaving,
    onMouseEnter,
    onMouseLeave,
    children,
    minWidth = 275,
}: Props) {
    const hoverWidth = Math.max(rect.width * 1.6, minWidth)
    let left = rect.left - containerRect.left + rect.width / 2 - hoverWidth / 2
    left = Math.max(0, Math.min(left, containerRect.width - hoverWidth))

    const originX =
        ((rect.left - containerRect.left + rect.width / 2 - left) /
            hoverWidth) *
        100

    const baseTop = rect.top - containerRect.top + rect.height / 2
    const cardRef = useRef<HTMLDivElement>(null)
    const [topAdjust, setTopAdjust] = useState(0)

    useLayoutEffect(() => {
        if (!cardRef.current) return
        const cardHeight = cardRef.current.offsetHeight
        const topInViewport = containerRect.top + baseTop - cardHeight / 2
        const bottomOverflow = topInViewport + cardHeight - viewportRect.bottom
        const topOverflow = viewportRect.top - topInViewport
        setTopAdjust(
            bottomOverflow > 0 ? bottomOverflow : topOverflow > 0 ? -topOverflow : 0,
        )
    }, [baseTop, containerRect.top, viewportRect.bottom, viewportRect.top])

    const style: React.CSSProperties = {
        left,
        width: `clamp(${minWidth}px, ${hoverWidth}px, 100%)`,
        top: baseTop - topAdjust,
        transformOrigin: `${originX}% 50%`,
    }

    return (
        <div
            ref={cardRef}
            className={`${classes.hoverCard} ${isLeaving ? classes.hoverCardLeaving : ''}`}
            style={style}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
        >
            {children}
        </div>
    )
}
