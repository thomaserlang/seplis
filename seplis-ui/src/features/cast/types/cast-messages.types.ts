import { PlayRequest } from '@/features/play/types/play-source.types'

export const CAST_NAMESPACE = 'urn:x-cast:seplis'
export const CAST_APP_ID =
    (import.meta as any).env?.VITE_CAST_APP_ID ?? '0BB2BE80'

export interface CastLoadData {
    playRequests: PlayRequest[]
    sourcePlayId: string
    sourceIndex: number
    audio: string | undefined
    subtitle: string | undefined
    maxBitrate: number
    startTime: number
    title: string | undefined
    secondaryTitle: string | undefined
}

// Messages FROM sender TO receiver
export type CastSenderMessage =
    | { type: 'setSubtitle'; subtitle: string | undefined }
    | { type: 'setAudio'; audio: string | undefined }
    | { type: 'setBitrate'; maxBitrate: number }
    | { type: 'setSource'; playId: string; sourceIndex: number }

// Messages FROM receiver TO sender
export type CastReceiverMessage = {
    type: 'status'
    currentTime: number
    duration: number
    isPaused: boolean
    isBuffering: boolean
}
