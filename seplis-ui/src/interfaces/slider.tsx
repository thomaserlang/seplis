
export interface ISliderItem<S = any> {
    key: any
    title: string | null | undefined
    img: string | null | undefined
    bottomText?: string | JSX.Element | null
    topText?: string | JSX.Element | null
    data?: S
}