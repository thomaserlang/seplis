import { AxiosError } from "axios"

export function ErrorMessageFromResponse(errorObj: any): JSX.Element {
    if (!errorObj)
        return <>Unknown error</>

    if (typeof errorObj === 'string')
        return <>{errorObj}</>
    
    if (errorObj.isAxiosError) {
        const e: AxiosError = errorObj
        const data = (e.response?.data as any)
        if (data?.message)
            return (e.response?.data as any)?.message
        if ((e.response.status == 422) && (data?.detail))
            return <>
                {data.detail.length > 0 && (
                    <ul>
                        {data.detail.map((error: any, index: any) => (
                        <li key={index}>
                            <strong>{error['loc'].join('.')}:</strong> {error['msg']}
                        </li>
                        ))}
                    </ul>)}
            </>
        return <>{e.message}</>
    }
    return <>{errorObj.message}</>
}