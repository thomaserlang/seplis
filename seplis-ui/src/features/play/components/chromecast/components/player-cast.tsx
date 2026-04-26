import { UsePlaySettings } from '@/features/play/hooks/use-play-settings'
import {
    PlayRequestSource,
    PlayRequestSources,
    PlaySourceStream,
} from '@/features/play/types/play-source.types'
import { ActionIcon, Flex, Tooltip } from '@mantine/core'
import { ArrowLeftIcon } from '@phosphor-icons/react'
import { useEffect, useRef, useState, type ReactNode } from 'react'
import { CAST_NAMESPACE } from '../constants'
import { useChromecast } from '../providers/chromecast-provider'
import { CastControls } from './cast-controls'
import { CastIdentity } from './cast-identity'
import { CastProgress } from './cast-progress'

interface Props {
    title?: string
    secondaryTitle?: string
    onClose?: () => void
    onPlayNext?: () => void
    playRequestSource: PlayRequestSource
    playRequestsSources: PlayRequestSources[]
    audio?: PlaySourceStream
    forceTranscode: boolean
    subtitle?: PlaySourceStream
    onSourceChange: (source: PlayRequestSource) => void
    onAudioChange: (audio: PlaySourceStream | undefined) => void
    onForceTranscodeChange: (value: boolean) => void
    onSubtitleChange: (subtitle: PlaySourceStream | undefined) => void
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
    playSettings: UsePlaySettings
}

export function PlayerCast({
    title,
    secondaryTitle,
    onClose,
    onPlayNext,
    playRequestSource,
    playRequestsSources,
    audio,
    forceTranscode,
    subtitle,
    onSourceChange,
    onAudioChange,
    onForceTranscodeChange,
    onSubtitleChange,
    preferredAudioLangs,
    preferredSubtitleLangs,
    playSettings,
}: Props): ReactNode {
    const {
        player,
        playerController,
        castSession,
        endSession,
        isConnected,
        sendMessage,
    } = useChromecast()
    const [subtitleOffset, setSubtitleOffset] = useState(0)

    useEffect(() => () => setSubtitleOffset(0), [])

    const sendSubtitleOffset = (offset: number) => {
        sendMessage(CAST_NAMESPACE, {
            type: 'subtitleOffset',
            offset,
        }).catch(() => {})
    }

    const [dragTime, setDragTime] = useState<number | null>(null)
    const [settingsOpen, setSettingsOpen] = useState(false)

    const currentTime = dragTime ?? player?.currentTime ?? 0
    const duration = player?.duration ?? 0
    const isPaused = player?.isPaused ?? true
    const canSeek = player?.canSeek ?? false
    const deviceName = castSession?.getCastDevice().friendlyName ?? 'Chromecast'
    const playerState = player?.playerState ?? null

    const prevPlayerStateRef = useRef<string | null>(null)
    useEffect(() => {
        if (playerState === prevPlayerStateRef.current) return
        prevPlayerStateRef.current = playerState
    })

    const formatTime = (secs: number) => {
        const h = Math.floor(secs / 3600)
        const m = Math.floor((secs % 3600) / 60)
        const s = Math.floor(secs % 60)
        if (h > 0)
            return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
        return `${m}:${String(s).padStart(2, '0')}`
    }

    const seek = (targetTime: number) => {
        if (!player || !playerController) return
        player.currentTime = Math.max(0, Math.min(targetTime, duration))
        playerController.seek()
    }

    return (
        <Flex
            direction="column"
            align="center"
            justify="center"
            p="md"
            gap="lg"
            style={{ position: 'relative' }}
        >
            {onClose && (
                <Tooltip label="Back" position="bottom">
                    <ActionIcon
                        variant="subtle"
                        size={44}
                        onClick={onClose}
                        aria-label="Close"
                        style={{ position: 'absolute', left: 0, top: 0 }}
                    >
                        <ArrowLeftIcon size={26} weight="bold" />
                    </ActionIcon>
                </Tooltip>
            )}

            <CastIdentity
                deviceName={deviceName}
                playerState={playerState}
                title={title}
                secondaryTitle={secondaryTitle}
            />

            <CastProgress
                currentTime={currentTime}
                duration={duration}
                canSeek={canSeek}
                onDragChange={setDragTime}
                onSeek={(v) => {
                    seek(v)
                    setDragTime(null)
                }}
                formatTime={formatTime}
            />

            <CastControls
                isPaused={isPaused}
                canSeek={canSeek}
                currentTime={currentTime}
                settingsOpen={settingsOpen}
                isConnected={isConnected}
                onSeek={seek}
                onPlayPause={() => playerController?.playOrPause()}
                onPlayNext={onPlayNext}
                onSettingsOpenChange={setSettingsOpen}
                onDisconnect={() => endSession(true)}
                playRequestSource={playRequestSource}
                playRequestsSources={playRequestsSources}
                audio={audio}
                forceTranscode={forceTranscode}
                subtitle={subtitle}
                subtitleOffset={subtitleOffset}
                canAdjustSubtitleOffset
                onSourceChange={onSourceChange}
                onAudioChange={onAudioChange}
                onForceTranscodeChange={onForceTranscodeChange}
                onSubtitleChange={onSubtitleChange}
                onSubtitleOffsetChange={(offset) => {
                    setSubtitleOffset(offset)
                    sendSubtitleOffset(offset)
                }}
                preferredAudioLangs={preferredAudioLangs}
                preferredSubtitleLangs={preferredSubtitleLangs}
                playSettings={playSettings}
            />
        </Flex>
    )
}
