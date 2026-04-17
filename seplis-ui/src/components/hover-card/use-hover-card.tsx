import { useCallback, useRef, useState } from 'react'
import { HoverCard } from './hover-card'

const SHOW_DELAY = 700
const HIDE_DELAY = 200

interface HoverState<T> {
    item: T
    rect: DOMRect
    containerRect: DOMRect
    viewportRect: DOMRect
    isLeaving: boolean
}

function intersectRect(base: DOMRect, next: DOMRect) {
    const top = Math.max(base.top, next.top)
    const bottom = Math.min(base.bottom, next.bottom)
    const left = Math.max(base.left, next.left)
    const right = Math.min(base.right, next.right)

    return new DOMRect(
        left,
        top,
        Math.max(0, right - left),
        Math.max(0, bottom - top),
    )
}

function getViewportRect(el: HTMLElement, containerRect: DOMRect) {
    let viewportRect = intersectRect(
        new DOMRect(0, 0, window.innerWidth, window.innerHeight),
        containerRect,
    )
    let current: HTMLElement | null = el.parentElement

    while (current) {
        const style = window.getComputedStyle(current)
        const clipsVertical =
            /(auto|scroll|hidden|clip)/.test(style.overflowY) ||
            /(auto|scroll|hidden|clip)/.test(style.overflow)

        if (clipsVertical) {
            viewportRect = intersectRect(
                viewportRect,
                current.getBoundingClientRect(),
            )
        }

        current = current.parentElement
    }

    return viewportRect
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
            if (hoverRef.current) {
                isHoveringRef.current = false
                setHover((h) => (h ? { ...h, isLeaving: true } : null))
                hideTimerRef.current = setTimeout(() => setHover(null), HIDE_DELAY)
            }
            showTimerRef.current = setTimeout(() => {
                const rect = el.getBoundingClientRect()
                const containerRect =
                    containerRef?.current?.getBoundingClientRect() ??
                    new DOMRect(0, 0, window.innerWidth, window.innerHeight)
                const viewportRect = getViewportRect(el, containerRect)
                isHoveringRef.current = true
                setHover({
                    item,
                    rect,
                    containerRect,
                    viewportRect,
                    isLeaving: false,
                })
            }, SHOW_DELAY)
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
        setHover((h) => (h ? { ...h, isLeaving: false } : null))
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
                viewportRect={hover.viewportRect}
                isLeaving={hover.isLeaving}
                onMouseEnter={onCardEnter}
                onMouseLeave={onItemLeave}
            >
                {renderContent(hover.item)}
            </HoverCard>
        ) : null

    return { getItemProps, portal, dismiss }
}
