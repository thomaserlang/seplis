export interface APIError {
    code: number
    message: string
    type: string
    errors: {
        field: string
        message: string
        type: string
        input: any
    }[]
}
