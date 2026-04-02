import { APIError } from '@/types/api-error.types'
import { Alert, Text } from '@mantine/core'
import { HTTPError } from 'ky'
import { ReactNode, useEffect, useState } from 'react'

interface Props {
    message?: string
    errorObj?: string | unknown
}

export function ErrorBox({ message, errorObj }: Props) {
    return (
        <Alert color="red">
            <Text span fw={600}>
                {message || errorMessageFromResponse(errorObj)}
            </Text>
        </Alert>
    )
}

export function errorMessageFromResponse(errorObj: any): ReactNode {
    if (!errorObj) return <>Unknown error</>

    if (typeof errorObj === 'string') return <>{errorObj}</>

    if (errorObj instanceof HTTPError) {
        return <HTTPErrorMessage error={errorObj} />
    }
    return <>{errorObj.message}</>
}

function HTTPErrorMessage({ error }: { error: HTTPError }) {
    const [message, setMessage] = useState<string | null>(null)

    useEffect(() => {
        if (
            error.response.headers
                .get('content-type')
                ?.includes('application/json')
        ) {
            error.response.json<APIError>().then((data) => {
                if (data?.message) setMessage(data.message)
            })
        }
    }, [error])

    return <>{message ?? error.message}</>
}
