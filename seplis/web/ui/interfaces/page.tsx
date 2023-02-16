export interface IPageCursorQuery {
    cursor: string | null
    per_page: number
}


export interface IPageCursorResult<T> {
    items: T[]
    cursor: string | null
}


export interface IPageCursorTotalResult<T> {
    items: T[]
    cursor: string | null
    total: number
}
