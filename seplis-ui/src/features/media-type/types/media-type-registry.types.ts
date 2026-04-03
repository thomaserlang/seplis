export type MediaType = 'series' | 'movie'

export interface MediaTypeRender {
    itemId: string
}

export interface MediaTypeInfo {
    name: string
    color: string
    mediaType: MediaType
    render: (props: MediaTypeRender) => React.ReactElement
}
