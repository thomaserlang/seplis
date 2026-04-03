import { errorMessageFromResponse } from '@/components/error-box'
import { notifications } from '@mantine/notifications'

type NotificationPosition =
    | 'top-left'
    | 'top-right'
    | 'top-center'
    | 'bottom-left'
    | 'bottom-right'
    | 'bottom-center'

export function toastSuccess(message: string, position?: NotificationPosition) {
    return notifications.show({
        title: message,
        message: '',
        color: 'green',
        autoClose: 2000,
        withBorder: true,
        position: position,
    })
}

export function toastError(errorObj: any, position?: NotificationPosition) {
    try {
        return notifications.show({
            title: errorMessageFromResponse(errorObj),
            message: '',
            color: 'red',
            autoClose: 5000,
            withBorder: true,
            position: position,
        })
    } catch (e) {
        console.error('Error showing toast', e)
    }
}

export function toastLoading(message: string, position?: NotificationPosition) {
    return notifications.show({
        title: message,
        message: '',
        loading: true,
        autoClose: false,
        withBorder: true,
        position: position,
    })
}

export function hideToast(id: string) {
    return notifications.hide(id)
}

export async function toastPromise({
    promise,
    loading,
    success = {},
    error = {},
    position,
}: {
    promise: Promise<any>
    loading: {
        title?: string
        message?: string
    }
    success?: {
        title?: string
        message?: string
        onSuccess?: () => void
    }
    error?: {
        title?: string
        message?: string
        onError?: (error: any) => void
    }
    position?: NotificationPosition
}) {
    const id = notifications.show({
        loading: true,
        title: loading.title,
        message: loading.message,
        autoClose: false,
        withBorder: true,
        position: position,
    })
    try {
        await promise
        if (!success.title && !success.message) {
            notifications.hide(id)
            return
        }
        notifications.update({
            id,
            loading: false,
            title: success.title,
            message: success.message,
            color: 'green',
            autoClose: 1500,
            position: position,
        })
        success.onSuccess?.()
    } catch (e) {
        notifications.update({
            id,
            loading: false,
            title: error?.title,
            message: error?.message || errorMessageFromResponse(e),
            color: 'red',
            autoClose: 5000,
            position: position,
        })
        error?.onError?.(e)
    }
}
