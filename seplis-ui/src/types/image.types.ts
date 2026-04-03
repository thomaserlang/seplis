export type ImageTypes = 'poster' | 'backdrop'

export interface IImage {
    id: number
    height: number
    width: number
    file_id: string
    type: ImageTypes
    created_at: string
    url: string
}
