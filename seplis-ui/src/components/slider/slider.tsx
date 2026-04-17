import { useHoverCard } from '@/components/hover-card/use-hover-card'
import posterClasses from '@/components/poster-page/poster-page.module.css'
import { MantineStyleProp, Skeleton } from '@mantine/core'
import { CaretLeftIcon, CaretRightIcon } from '@phosphor-icons/react'
import { useCallback, useEffect, useRef, useState } from 'react'
import classes from './slider.module.css'
import { SliderProps } from './slider.types'

export function Slider<T>({
    items,
    renderItem,
    renderHoverCard,
    isLoading = false,
    onLoadMore,
    title,
    skeletonCount = 24,
    skeletonAspectRatio,
    itemWidth,
    startPadding,
    background,
    onClick,
    emptyMessage,
}: SliderProps<T>) {
    const scrollRef = useRef<HTMLDivElement>(null)
    const sentinelRef = useRef<HTMLDivElement>(null)
    const containerRef = useRef<HTMLDivElement>(null)
    const isLoadingRef = useRef(isLoading)

    const [canScrollLeft, setCanScrollLeft] = useState(false)
    const [canScrollRight, setCanScrollRight] = useState(false)

    const { getItemProps, portal } = useHoverCard({
        renderContent: renderHoverCard,
        containerRef,
    })

    useEffect(() => {
        isLoadingRef.current = isLoading
    }, [isLoading])

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
        }
        el.addEventListener('scroll', onScroll, { passive: true })
        const ro = new ResizeObserver(syncScrollState)
        ro.observe(el)
        return () => {
            el.removeEventListener('scroll', onScroll)
            ro.disconnect()
        }
    }, [syncScrollState])

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

    const isEmpty = !isLoading && items.length === 0

    if (isEmpty && !emptyMessage) return null

    const styleVars: MantineStyleProp = {}

    if (itemWidth) {
        styleVars['--slider-item-width'] = itemWidth
    }
    if (startPadding) {
        styleVars['--slider-start-padding'] = startPadding
    }
    if (background) {
        styleVars['--slider-background'] = background
    }

    const style =
        Object.keys(styleVars).length > 0
            ? (styleVars as React.CSSProperties)
            : undefined
    const skeletonStyle = skeletonAspectRatio
        ? ({ aspectRatio: skeletonAspectRatio } as React.CSSProperties)
        : undefined

    return (
        <div ref={containerRef} className={classes.root} style={style}>
            {title && <div className={classes.title}>{title}</div>}
            {isEmpty && (
                <div className={classes.emptyMessage}>{emptyMessage}</div>
            )}
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
                            className={`${posterClasses.item} ${classes.item}`}
                            {...getItemProps(item)}
                            onClick={onClick ? () => onClick(item) : undefined}
                            style={{ cursor: onClick ? 'pointer' : undefined }}
                        >
                            {renderItem(item, index)}
                        </div>
                    ))}

                    {isLoading &&
                        Array.from({ length: skeletonCount }).map((_, i) => (
                            <div
                                key={`sk-${i}`}
                                className={classes.skeletonItem}
                                style={skeletonStyle}
                            >
                                <Skeleton height="100%" radius="sm" />
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

            {portal}
        </div>
    )
}
