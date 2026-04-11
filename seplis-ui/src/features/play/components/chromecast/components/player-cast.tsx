import { UsePlaySettings } from '@/features/play/hooks/use-play-settings'
import {
    PlayRequestSource,
    PlayRequestSources,
} from '@/features/play/types/play-source.types'
import { ActionIcon, Flex, Tooltip } from '@mantine/core'
import { ArrowLeftIcon } from '@phosphor-icons/react'
import { useEffect, useRef, useState, type ReactNode } from 'react'
import { useChromecast } from '../providers/chromecast-provider'
import { CastControls } from './cast-controls'
import { CastIdentity } from './cast-identity'
import { CastProgress } from './cast-progress'

const CAST_NAMESPACE = 'urn:x-cast:seplis.player'

interface Props {
    title?: string
    secondaryTitle?: string
    onClose?: () => void
    playRequestSource: PlayRequestSource
    playRequestsSources: PlayRequestSources[]
    audio: string | undefined
    forceTranscode: boolean
    activeSubtitleKey: string | undefined
    onSourceChange: (source: PlayRequestSource) => void
    onAudioChange: (audio: string | undefined) => void
    onForceTranscodeChange: (value: boolean) => void
    onSubtitleChange: (key: string | undefined) => void
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
    playSettings: UsePlaySettings
}

export function PlayerCast({
    title,
    secondaryTitle,
    onClose,
    playRequestSource,
    playRequestsSources,
    audio,
    forceTranscode,
    activeSubtitleKey,
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
        })
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
                onSettingsOpenChange={setSettingsOpen}
                onDisconnect={() => endSession(true)}
                playRequestSource={playRequestSource}
                playRequestsSources={playRequestsSources}
                audioLang={audio}
                forceTranscode={forceTranscode}
                activeSubtitleKey={activeSubtitleKey}
                subtitleOffset={subtitleOffset}
                onSourceChange={onSourceChange}
                onAudioLangChange={onAudioChange}
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
