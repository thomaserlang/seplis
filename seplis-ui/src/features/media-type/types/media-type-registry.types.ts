export type MediaType = 'series' | 'movie' | 'episode'

export interface MediaTypeRender {
    itemId: string
}

export interface MediaTypeHoverCard<T = any> {
    data: T
}

export interface MediaTypeInfo<T = any> {
    name: string
    color: string
    accentHue: number
    mediaType: MediaType
    render: (props: MediaTypeRender) => React.ReactElement
    renderHoverCard: (props: MediaTypeHoverCard<T>) => React.ReactElement
    player?: (props: {
        itemId: string
        onClose: () => void
    }) => React.ReactElement
}
