export type ImageTypes = 'poster' | 'backdrop'


export interface IImageCreate {
    external_name: string | null
    external_id: string | null
}


export interface IImage extends IImageCreate {
    id: number
    height: number
    width: number
    hash: string
    type: ImageTypes
    created_at: Date
    url: string
}