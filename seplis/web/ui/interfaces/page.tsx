export interface IPageCursorQuery {
    before: string | null
    after: string | null
    first: number
}
  

export interface IPageCursorResult<T> {
    items: T[]
    cursor: string | null
}

export interface IPageQuery {
    page: number
    per_page: number
}

export interface IPageLinks {
    next: string | null
    prev: string | null
    first: string | null
    last: string | null
}

export interface IPageResult<T> {
    items: T[]
    links: IPageLinks
    total: number
    per_page: number
    page: number
    pages: number
}