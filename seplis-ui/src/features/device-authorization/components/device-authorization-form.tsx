import { ErrorBox } from '@/components/error-box'
import { useActiveUser } from '@/features/user/api/session.store'
import { PinInput, Stack, Text } from '@mantine/core'
import { useMediaQuery } from '@mantine/hooks'
import type { FormEvent } from 'react'
import { useState } from 'react'
import { useApproveDeviceAuthorization } from '../api/device-authorization.api'
import { DeviceAuthorizationAction } from './device-authorization-action'

interface Props {
    initialCode: string
    onAuthorized: () => void
}

function normalizeCode(value: string) {
    return value.replace(/\D/g, '').slice(0, 6)
}

export function DeviceAuthorizationForm({ initialCode, onAuthorized }: Props) {
    const [user] = useActiveUser()
    const isNarrow = useMediaQuery('(max-width: 30em)')
    const [code, setCode] = useState(initialCode)
    const approval = useApproveDeviceAuthorization({
        onSuccess: onAuthorized,
    })

    const authorize = (value: string) => {
        const userCode = normalizeCode(value)
        if (!user || userCode.length !== 6 || approval.isPending) return
        approval.mutate({ data: { user_code: userCode } })
    }

    const submit = (event: FormEvent) => {
        event.preventDefault()
        authorize(code)
    }

    return (
        <Stack component="form" onSubmit={submit} gap="lg">
            <Text c="dimmed">Enter the code shown on your device.</Text>
            <PinInput
                length={6}
                type="number"
                oneTimeCode
                size={isNarrow ? 'md' : 'lg'}
                gap={isNarrow ? 'xs' : 'sm'}
                value={code}
                disabled={approval.isPending}
                onComplete={authorize}
                onChange={(value) => {
                    setCode(normalizeCode(value))
                    approval.reset()
                }}
                ariaLabel="Device authorization code"
            />
            {approval.error && <ErrorBox errorObj={approval.error} />}
            <DeviceAuthorizationAction
                authenticated={Boolean(user)}
                code={code}
                isPending={approval.isPending}
            />
        </Stack>
    )
}
