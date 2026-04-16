import { APIError } from '@/types/api-error.types'
import { Alert, Text } from '@mantine/core'
import { HTTPError } from 'ky'
import { ReactNode } from 'react'

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
        const error = errorObj.data as APIError

        if (typeof errorObj.data === 'string' && errorObj.data) {
            return <>{errorObj.data}</>
        }

        if (error && error.message) return error.message
        if (errorObj.data) return <pre>{JSON.stringify(errorObj.data, null, 2)}</pre>

        return <>{errorObj.message}</>
    }

    if (
        typeof errorObj === 'object' &&
        'message' in errorObj &&
        typeof errorObj.message === 'string'
    ) {
        return <>{errorObj.message}</>
    }

    return <>{String(errorObj)}</>
}
