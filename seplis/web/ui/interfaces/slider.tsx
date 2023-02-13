
export interface ISliderItem<S = any> {
    key: any
    title: string
    img: string
    bottomText?: string | JSX.Element
    topText?: string | JSX.Element
    data?: S
}