// Singleton that loads the Cast Sender SDK once and notifies subscribers.
import { CAST_APP_ID } from './types/cast-messages.types'

const SDK_URL =
    'https://www.gstatic.com/cv/js/sender/v1/cast_sender.js?loadCastFramework=1'

let ready = false
let initialized = false
const callbacks: Array<() => void> = []

export function onCastSdkReady(cb: () => void): void {
    if (ready) {
        cb()
        return
    }
    callbacks.push(cb)
    if (document.querySelector(`script[src="${SDK_URL}"]`)) return

    ;(window as any).__onGCastApiAvailable = (isAvailable: boolean) => {
        if (!isAvailable) return
        ready = true
        callbacks.forEach((fn) => fn())
        callbacks.length = 0
    }

    const script = document.createElement('script')
    script.src = SDK_URL
    document.head.appendChild(script)
}

/** Initialize CastContext exactly once, safe to call multiple times. */
export function initCastContext(): void {
    if (initialized) return
    const castFramework = (window as any).cast?.framework
    if (!castFramework) return
    initialized = true
    castFramework.CastContext.getInstance().setOptions({
        receiverApplicationId: CAST_APP_ID,
        // AutoJoinPolicy lives on chrome.cast, not cast.framework — use the string directly
        autoJoinPolicy: 'origin_scoped',
    })
}
