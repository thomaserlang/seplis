export interface SliderProps<T> {
    items: T[]
    renderItem: (item: T, index: number) => React.ReactNode
    renderHoverCard?: (item: T) => React.ReactNode
    isLoading?: boolean
    onLoadMore?: () => void
    title?: React.ReactNode
    skeletonCount?: number
    itemWidth?: string
}

export interface HoverState<T> {
    item: T
    rect: DOMRect
    isLeaving: boolean
}
