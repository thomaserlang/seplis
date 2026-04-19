import { useEffect, useRef } from 'react'
import { useSessionActions } from '../api/session.store'

export function useAddUserPopup() {
    const { refreshSession } = useSessionActions()
    const popupPollInterval = useRef<number | null>(null)

    useEffect(() => {
        return () => {
            if (popupPollInterval.current !== null) {
                window.clearInterval(popupPollInterval.current)
            }
        }
    }, [])

    const openAddUserPopup = () => {
        const popup = window.open(
            '/login?popup=1',
            'seplis-add-user',
            'popup=yes,width=500,height=720,resizable=yes,scrollbars=yes',
        )
        if (!popup) return

        if (popupPollInterval.current !== null) {
            window.clearInterval(popupPollInterval.current)
        }

        popupPollInterval.current = window.setInterval(() => {
            if (!popup.closed) return

            if (popupPollInterval.current !== null) {
                window.clearInterval(popupPollInterval.current)
                popupPollInterval.current = null
            }
            refreshSession()
        }, 500)
    }

    return {
        openAddUserPopup,
    }
}
