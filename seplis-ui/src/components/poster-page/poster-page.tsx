import { ScrollArea, Skeleton } from '@mantine/core'
import { useHoverCard } from '../hover-card/use-hover-card'
import classes from './poster-page.module.css'

interface Props<T> {
    items: T[]
    renderItem: (item: T) => React.ReactNode
    renderHoverCard?: (item: T) => React.ReactNode
    isLoading?: boolean
    onLoadMore?: () => void
    onClick?: (item: T) => void
    skeletonCount?: number
}

export function PosterPage<T>({
    items,
    renderItem,
    renderHoverCard,
    isLoading,
    onLoadMore,
    onClick,
    skeletonCount = 9,
}: Props<T>) {
    const { getItemProps, portal, dismiss } = useHoverCard(renderHoverCard)

    return (
        <ScrollArea onBottomReached={onLoadMore}>
            <div className={classes.grid}>
                {items.map((item, index) => (
                    <div
                        key={index}
                        {...getItemProps(item)}
                        onClick={() => {
                            onClick?.(item)
                            dismiss()
                        }}
                    >
                        {renderItem(item)}
                    </div>
                ))}
                {portal}
                {isLoading &&
                    new Array(skeletonCount)
                        .fill(0)
                        .map((_, i) => (
                            <Skeleton key={i} height="100%" radius="sm" />
                        ))}
            </div>
        </ScrollArea>
    )
}
