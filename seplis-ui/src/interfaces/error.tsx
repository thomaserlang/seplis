export interface IError<E = any> {
    code: number
    message: string
    errors: E[]
}

export interface IValidationError {
    field: string[]
    message: string
}