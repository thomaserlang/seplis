export type MediaType = 'series' | 'movie'

export interface MediaTypeRender {
    itemId: string
}

export interface MediaTypeHoverCard<T = any> {
    data: T
}

export interface MediaTypeInfo<T = any> {
    name: string
    color: string
    mediaType: MediaType
    render: (props: MediaTypeRender) => React.ReactElement
    renderHoverCard: (props: MediaTypeHoverCard<T>) => React.ReactElement
}
