import { useCallback, useRef, useState } from 'react'
import { HoverCard } from './hover-card'

const SHOW_DELAY = 700
const HIDE_DELAY = 700

interface HoverState<T> {
    item: T
    rect: DOMRect
    containerRect: DOMRect
    isLeaving: boolean
}

export function useHoverCard<T>({
    renderContent,
    containerRef,
}: {
    renderContent?: (item: T) => React.ReactNode
    containerRef?: React.RefObject<HTMLElement | null>
}) {
    const isHoveringRef = useRef(false)
    const showTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const hideTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const [hover, setHover] = useState<HoverState<T> | null>(null)
    const hoverRef = useRef(hover)
    hoverRef.current = hover

    const clearTimers = useCallback(() => {
        if (showTimerRef.current) {
            clearTimeout(showTimerRef.current)
            showTimerRef.current = null
        }
        if (hideTimerRef.current) {
            clearTimeout(hideTimerRef.current)
            hideTimerRef.current = null
        }
    }, [])

    const onItemEnter = useCallback(
        (item: T, el: HTMLElement) => {
            if (!renderContent) return
            clearTimers()
            const delay = isHoveringRef.current ? HIDE_DELAY : SHOW_DELAY
            showTimerRef.current = setTimeout(() => {
                const rect = el.getBoundingClientRect()
                const containerRect =
                    containerRef?.current?.getBoundingClientRect() ??
                    new DOMRect(0, 0, window.innerWidth, window.innerHeight)
                isHoveringRef.current = true
                setHover({ item, rect, containerRect, isLeaving: false })
            }, delay)
        },
        [clearTimers, renderContent, containerRef],
    )

    const onItemLeave = useCallback(() => {
        clearTimers()
        setHover((h) => (h ? { ...h, isLeaving: true } : null))
        hideTimerRef.current = setTimeout(() => {
            isHoveringRef.current = false
            setHover(null)
        }, HIDE_DELAY)
    }, [clearTimers])

    const onCardEnter = useCallback(() => {
        clearTimers()
        if (hoverRef.current?.isLeaving) {
            isHoveringRef.current = false
            setHover(null)
        } else {
            setHover((h) => (h ? { ...h, isLeaving: false } : null))
        }
    }, [clearTimers])

    const dismiss = useCallback(() => {
        clearTimers()
        isHoveringRef.current = false
        setHover(null)
    }, [clearTimers])

    const getItemProps = useCallback(
        (item: T) =>
            renderContent
                ? {
                      onMouseEnter: (e: React.MouseEvent<HTMLElement>) =>
                          onItemEnter(item, e.currentTarget),
                      onMouseLeave: onItemLeave,
                  }
                : {},
        [onItemEnter, onItemLeave, renderContent],
    )

    const portal =
        hover && renderContent ? (
            <HoverCard
                rect={hover.rect}
                containerRect={hover.containerRect}
                isLeaving={hover.isLeaving}
                onMouseEnter={onCardEnter}
                onMouseLeave={onItemLeave}
            >
                {renderContent(hover.item)}
            </HoverCard>
        ) : null

    return { getItemProps, portal, dismiss }
}
