import type { ChromecastMessage } from '../types'

export function parseChromecastMessage(message: ChromecastMessage | string) {
    try {
        return typeof message === 'string'
            ? (JSON.parse(message) as ChromecastMessage)
            : message
    } catch {
        return null
    }
}
