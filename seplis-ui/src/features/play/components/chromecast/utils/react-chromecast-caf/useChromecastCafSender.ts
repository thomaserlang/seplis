import { useEffect, useState } from 'react'
import type { SenderCast, SenderChrome } from './sender-capture'

export type Sender = {
    cast: SenderCast
    chrome: SenderChrome
}

type SenderLoadResult =
    | {
          status: 'ready'
          cast: SenderCast
          chrome: SenderChrome
      }
    | {
          status: 'unavailable' | 'error'
          cast: null
          chrome: null
          reason?: string
      }

type SenderState =
    | {
          status: 'loading'
          cast: null
          chrome: null
          reason?: undefined
      }
    | SenderLoadResult

const SCRIPT_ID = 'chromecast-caf-sender'
const SCRIPT_SRC =
    'https://www.gstatic.com/cv/js/sender/v1/cast_sender.js?loadCastFramework=1'
const LOAD_TIMEOUT_MS = 10_000

const load = (() => {
    let promise: Promise<SenderLoadResult> | null = null

    return () => {
        if (promise === null) {
            promise = new Promise((resolve) => {
                let settled = false
                const finish = (result: SenderLoadResult) => {
                    if (settled) return
                    settled = true
                    window.clearTimeout(timeoutId)
                    resolve(result)
                }
                const timeoutId = window.setTimeout(() => {
                    finish({
                        status: 'error',
                        cast: null,
                        chrome: null,
                        reason: 'Timed out loading Google Cast sender SDK',
                    })
                }, LOAD_TIMEOUT_MS)

                if ('cast' in window && 'framework' in cast) {
                    finish({
                        status: 'ready',
                        cast,
                        chrome,
                    })
                    return
                }

                const previousCallback = window.__onGCastApiAvailable
                window.__onGCastApiAvailable = (isAvailable) => {
                    if (isAvailable) {
                        finish({
                            status: 'ready',
                            cast,
                            chrome,
                        })
                        return
                    }

                    finish({
                        status: 'unavailable',
                        cast: null,
                        chrome: null,
                        reason: 'Google Cast API is unavailable',
                    })
                }
                if (previousCallback) {
                    const currentCallback = window.__onGCastApiAvailable
                    window.__onGCastApiAvailable = (isAvailable, reason) => {
                        try {
                            previousCallback(isAvailable, reason)
                        } catch {}
                        currentCallback(isAvailable, reason)
                    }
                }

                const existing = document.getElementById(SCRIPT_ID)
                if (existing) return

                const script = document.createElement('script')
                script.id = SCRIPT_ID
                script.async = true
                script.src = SCRIPT_SRC
                script.onerror = () => {
                    finish({
                        status: 'error',
                        cast: null,
                        chrome: null,
                        reason: 'Failed to load Google Cast sender SDK',
                    })
                }
                document.body.appendChild(script)
            })
        }
        return promise
    }
})()

export const useChromecastCafSender = () => {
    const [sender, setSender] = useState<SenderState>({
        status: 'loading',
        cast: null,
        chrome: null,
    })

    useEffect(() => {
        let mounted = true
        load().then((sender) => {
            if (mounted) setSender(sender)
        })

        return () => {
            mounted = false
        }
    }, [])

    return sender
}
