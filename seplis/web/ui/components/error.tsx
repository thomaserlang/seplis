import { AxiosError } from "axios"

export function ErrorMessageFromResponse(errorObj: any): string {
    console.log(errorObj)
    if (!errorObj)
        return 'Unknown error'

    if (typeof errorObj === 'string')
        return errorObj
    
    if (errorObj.isAxiosError) {
        const e: AxiosError = errorObj
        if ((e.response?.data as any)?.message)
            return (e.response?.data as any)?.message
        return e.message
    }
    return errorObj.message
}