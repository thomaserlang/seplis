import { AxiosError } from "axios"

export function ErrorMessageFromResponse(errorObj: any): JSX.Element {
    if (!errorObj)
        return <>Unknown error</>

    if (typeof errorObj === 'string')
        return <>{errorObj}</>

    if (errorObj.isAxiosError) {
        const e: AxiosError = errorObj
        const data = (e.response?.data as any)
        if (data?.code == 1001) {
            return <>
                {data.errors.length > 0 && (
                    <ul>
                        {data.errors.map((error: any, index: any) => (
                            <li key={index}>
                                {error['field'].join('.')}: {error['message']}
                            </li>
                        ))}
                    </ul>
                )}
            </>
        } 
        else if (data?.detail)
            return data.detail
        else if (data?.message)
            return data.message
        return <>{e.message}</>
    }
    return <>{errorObj.message}</>
}