import { Skeleton } from '@mantine/core'
import { useEffect, useRef } from 'react'
import { useHoverCard } from '../hover-card/use-hover-card'
import classes from './poster-page.module.css'

interface Props<T> {
    items: T[]
    renderItem: (item: T) => React.ReactNode
    renderHoverCard?: (item: T) => React.ReactNode
    isLoading?: boolean
    onLoadMore?: () => void
    hasMore?: boolean
    onClick?: (item: T) => void
    skeletonCount?: number
}

export function PosterPage<T>({
    items,
    renderItem,
    renderHoverCard,
    isLoading,
    onLoadMore,
    hasMore,
    onClick,
    skeletonCount = 9,
}: Props<T>) {
    const containerRef = useRef<HTMLDivElement>(null)
    const loadMoreRef = useRef<HTMLDivElement>(null)
    const { getItemProps, portal, dismiss } = useHoverCard(renderHoverCard, containerRef)

    useEffect(() => {
        if (!onLoadMore || !hasMore || isLoading || !loadMoreRef.current) return

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry?.isIntersecting) {
                    onLoadMore()
                }
            },
            {
                rootMargin: '400px 0px',
            },
        )

        observer.observe(loadMoreRef.current)

        return () => observer.disconnect()
    }, [hasMore, isLoading, onLoadMore])

    return (
        <div ref={containerRef} className={classes.grid}>
            {items.map((item, index) => (
                <div
                    key={index}
                    {...getItemProps(item)}
                    onClick={() => {
                        onClick?.(item)
                        dismiss()
                    }}
                    className={classes.item}
                >
                    {renderItem(item)}
                </div>
            ))}
            {portal}
            {isLoading &&
                Array.from({ length: skeletonCount }, (_, i) => (
                    <Skeleton key={i} height="100%" radius="sm" />
                ))}
            {hasMore && <div ref={loadMoreRef} className={classes.loadMoreTrigger} />}
        </div>
    )
}
