import { Alert } from '@mantine/core'
import { CheckCircleIcon } from '@phosphor-icons/react'

export function DeviceAuthorizationSuccess() {
    return (
        <Alert
            color="green"
            icon={<CheckCircleIcon size={22} />}
            title="Device authorized"
        >
            You can return to your device.
        </Alert>
    )
}
