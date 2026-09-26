import { Button } from '@mantine/core'
import { CheckCircleIcon, SignInIcon } from '@phosphor-icons/react'
import { Link } from 'react-router-dom'

interface Props {
    authenticated: boolean
    code: string
    isPending: boolean
}

export function DeviceAuthorizationAction({
    authenticated,
    code,
    isPending,
}: Props) {
    if (!authenticated) {
        const returnPath = `/device${code ? `?code=${code}` : ''}`

        return (
            <Button
                component={Link}
                to={`/login?next=${encodeURIComponent(returnPath)}`}
                leftSection={<SignInIcon size={18} />}
            >
                Log in to authorize
            </Button>
        )
    }

    return (
        <Button
            type="submit"
            leftSection={<CheckCircleIcon size={18} />}
            loading={isPending}
            disabled={code.length !== 6}
        >
            Authorize
        </Button>
    )
}
