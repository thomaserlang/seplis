import { Skeleton } from '@mantine/core'
import { CaretLeftIcon, CaretRightIcon } from '@phosphor-icons/react'
import { useCallback, useEffect, useRef, useState } from 'react'
import classes from './slider.module.css'

export interface SliderProps<T> {
    items: T[]
    renderItem: (item: T, index: number) => React.ReactNode
    isLoading?: boolean
    onLoadMore?: () => void
    title?: React.ReactNode
    skeletonCount?: number
    itemWidth?: string
}

export function Slider<T>({
    items,
    renderItem,
    isLoading = false,
    onLoadMore,
    title,
    skeletonCount = 24,
    itemWidth,
}: SliderProps<T>) {
    const scrollRef = useRef<HTMLDivElement>(null)
    const sentinelRef = useRef<HTMLDivElement>(null)
    const isLoadingRef = useRef(isLoading)
    const [canScrollLeft, setCanScrollLeft] = useState(false)
    const [canScrollRight, setCanScrollRight] = useState(false)

    useEffect(() => {
        isLoadingRef.current = isLoading
    }, [isLoading])

    const syncScrollState = useCallback(() => {
        const el = scrollRef.current
        if (!el) return
        setCanScrollLeft(el.scrollLeft > 4)
        setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 4)
    }, [])

    // Recompute after DOM updates driven by items/loading changes
    useEffect(() => {
        const id = requestAnimationFrame(syncScrollState)
        return () => cancelAnimationFrame(id)
    }, [items, isLoading, syncScrollState])

    useEffect(() => {
        const el = scrollRef.current
        if (!el) return
        el.addEventListener('scroll', syncScrollState, { passive: true })
        const ro = new ResizeObserver(syncScrollState)
        ro.observe(el)
        return () => {
            el.removeEventListener('scroll', syncScrollState)
            ro.disconnect()
        }
    }, [syncScrollState])

    // Infinite-scroll sentinel — uses a ref for isLoading to avoid
    // recreating the observer on every load-state toggle
    useEffect(() => {
        const sentinel = sentinelRef.current
        const scroll = scrollRef.current
        if (!onLoadMore || !sentinel || !scroll) return

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !isLoadingRef.current) {
                    onLoadMore()
                }
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
                        <div key={index} className={classes.item}>
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
        </div>
    )
}
