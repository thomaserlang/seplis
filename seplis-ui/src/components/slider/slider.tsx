import { Skeleton } from '@mantine/core'
import { CaretLeftIcon, CaretRightIcon } from '@phosphor-icons/react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { SliderHoverCard } from './slider-hover-card'
import classes from './slider.module.css'
import { HoverState, SliderProps } from './slider.types'

const SHOW_DELAY = 700
const HIDE_DELAY = 700

export function Slider<T>({
    items,
    renderItem,
    renderHoverCard,
    isLoading = false,
    onLoadMore,
    title,
    skeletonCount = 24,
    itemWidth,
}: SliderProps<T>) {
    const scrollRef = useRef<HTMLDivElement>(null)
    const sentinelRef = useRef<HTMLDivElement>(null)
    const isLoadingRef = useRef(isLoading)
    const isHoveringRef = useRef(false)
    const showTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const hideTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    const [canScrollLeft, setCanScrollLeft] = useState(false)
    const [canScrollRight, setCanScrollRight] = useState(false)
    const [hover, setHover] = useState<HoverState<T> | null>(null)
    const hoverRef = useRef(hover)
    hoverRef.current = hover

    useEffect(() => {
        isLoadingRef.current = isLoading
    }, [isLoading])

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

    const syncScrollState = useCallback(() => {
        const el = scrollRef.current
        if (!el) return
        setCanScrollLeft(el.scrollLeft > 4)
        setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 4)
    }, [])

    useEffect(() => {
        const id = requestAnimationFrame(syncScrollState)
        return () => cancelAnimationFrame(id)
    }, [items, isLoading, syncScrollState])

    useEffect(() => {
        const el = scrollRef.current
        if (!el) return
        const onScroll = () => {
            syncScrollState()
            clearTimers()
            isHoveringRef.current = false
            setHover(null)
        }
        el.addEventListener('scroll', onScroll, { passive: true })
        const ro = new ResizeObserver(syncScrollState)
        ro.observe(el)
        return () => {
            el.removeEventListener('scroll', onScroll)
            ro.disconnect()
        }
    }, [syncScrollState, clearTimers])

    useEffect(() => {
        const sentinel = sentinelRef.current
        const scroll = scrollRef.current
        if (!onLoadMore || !sentinel || !scroll) return
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !isLoadingRef.current) onLoadMore()
            },
            { root: scroll, rootMargin: '0px 300px 0px 0px', threshold: 0 },
        )
        observer.observe(sentinel)
        return () => observer.disconnect()
    }, [onLoadMore])

    const scrollBy = useCallback((direction: 'left' | 'right') => {
        const el = scrollRef.current
        if (!el) return
        el.scrollBy({
            left:
                direction === 'right'
                    ? el.clientWidth * 0.8
                    : -(el.clientWidth * 0.8),
            behavior: 'smooth',
        })
    }, [])

    const handleItemEnter = useCallback(
        (item: T, el: HTMLElement) => {
            if (!renderHoverCard) return
            clearTimers()
            const delay = isHoveringRef.current ? HIDE_DELAY : SHOW_DELAY
            showTimerRef.current = setTimeout(() => {
                const rect = el.getBoundingClientRect()
                isHoveringRef.current = true
                setHover({ item, rect, isLeaving: false })
            }, delay)
        },
        [clearTimers, renderHoverCard],
    )

    const handleLeave = useCallback(() => {
        clearTimers()
        setHover((h) => (h ? { ...h, isLeaving: true } : null))
        hideTimerRef.current = setTimeout(() => {
            isHoveringRef.current = false
            setHover(null)
        }, HIDE_DELAY)
    }, [clearTimers])

    const handleHoverCardEnter = useCallback(() => {
        clearTimers()
        if (hoverRef.current?.isLeaving) {
            isHoveringRef.current = false
            setHover(null)
        } else {
            setHover((h) => (h ? { ...h, isLeaving: false } : null))
        }
    }, [clearTimers])

    const style = itemWidth
        ? ({ '--slider-item-width': itemWidth } as React.CSSProperties)
        : undefined

    return (
        <div className={classes.root} style={style}>
            {title && <div className={classes.title}>{title}</div>}
            <div className={classes.track}>
                {canScrollLeft && (
                    <button
                        className={`${classes.arrow} ${classes.arrowLeft}`}
                        onClick={() => scrollBy('left')}
                        aria-label="Scroll left"
                    >
                        <CaretLeftIcon size={22} weight="bold" />
                    </button>
                )}

                <div ref={scrollRef} className={classes.scroll}>
                    {items.map((item, index) => (
                        <div
                            key={index}
                            className={classes.item}
                            onMouseEnter={
                                renderHoverCard
                                    ? (e) =>
                                          handleItemEnter(item, e.currentTarget)
                                    : undefined
                            }
                            onMouseLeave={
                                renderHoverCard ? handleLeave : undefined
                            }
                        >
                            {renderItem(item, index)}
                        </div>
                    ))}

                    {isLoading &&
                        Array.from({ length: skeletonCount }).map((_, i) => (
                            <div
                                key={`sk-${i}`}
                                className={classes.skeletonItem}
                            >
                                <Skeleton height="100%" radius="md" />
                            </div>
                        ))}

                    {onLoadMore && (
                        <div
                            ref={sentinelRef}
                            className={classes.sentinel}
                            aria-hidden
                        />
                    )}
                </div>

                {canScrollRight && (
                    <button
                        className={`${classes.arrow} ${classes.arrowRight}`}
                        onClick={() => scrollBy('right')}
                        aria-label="Scroll right"
                    >
                        <CaretRightIcon size={22} weight="bold" />
                    </button>
                )}
            </div>

            {hover &&
                renderHoverCard &&
                createPortal(
                    <SliderHoverCard
                        rect={hover.rect}
                        isLeaving={hover.isLeaving}
                        onMouseEnter={handleHoverCardEnter}
                        onMouseLeave={handleLeave}
                    >
                        {renderHoverCard(hover.item)}
                    </SliderHoverCard>,
                    document.body,
                )}
        </div>
    )
}
