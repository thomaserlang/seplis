import {
    PlayerSettings,
    PlayerSettingsProps,
} from '@/features/play/components/player-settings'
import { ActionIcon, Group, Popover, Tooltip } from '@mantine/core'
import {
    ArrowClockwiseIcon,
    ArrowCounterClockwiseIcon,
    GearIcon,
    PauseIcon,
    PlayIcon,
    ScreencastIcon,
} from '@phosphor-icons/react'
import type { ReactNode } from 'react'

const SEEK_TIME = 10

interface Props extends PlayerSettingsProps {
    isPaused: boolean
    canSeek: boolean
    currentTime: number
    settingsOpen: boolean
    isConnected: boolean
    onSeek: (time: number) => void
    onPlayPause: () => void
    onSettingsOpenChange: (open: boolean) => void
    onDisconnect: () => void
}

export function CastControls({
    isPaused,
    canSeek,
    currentTime,
    settingsOpen,
    isConnected,
    onSeek,
    onPlayPause,
    onSettingsOpenChange,
    onDisconnect,
    ...settingsProps
}: Props): ReactNode {
    return (
        <>
            <Group gap="md" justify="center">
                <Tooltip label={`Seek back ${SEEK_TIME}s`} position="top">
                    <ActionIcon
                        variant="subtle"
                        size="xl"
                        aria-label={`Seek back ${SEEK_TIME}s`}
                        disabled={!canSeek}
                        onClick={() => onSeek(currentTime - SEEK_TIME)}
                    >
                        <ArrowCounterClockwiseIcon size={22} weight="bold" />
                    </ActionIcon>
                </Tooltip>
                <Tooltip label={isPaused ? 'Play' : 'Pause'} position="top">
                    <ActionIcon
                        variant="filled"
                        size={56}
                        radius="xl"
                        aria-label={isPaused ? 'Play' : 'Pause'}
                        onClick={onPlayPause}
                    >
                        {isPaused ? (
                            <PlayIcon size={26} weight="fill" />
                        ) : (
                            <PauseIcon size={26} weight="fill" />
                        )}
                    </ActionIcon>
                </Tooltip>
                <Tooltip label={`Seek forward ${SEEK_TIME}s`} position="top">
                    <ActionIcon
                        variant="subtle"
                        size="xl"
                        aria-label={`Seek forward ${SEEK_TIME}s`}
                        disabled={!canSeek}
                        onClick={() => onSeek(currentTime + SEEK_TIME)}
                    >
                        <ArrowClockwiseIcon size={22} weight="bold" />
                    </ActionIcon>
                </Tooltip>
            </Group>

            <Group gap={4} justify="center">
                {isConnected && (
                    <Tooltip label="Disconnect Chromecast" position="top">
                        <ActionIcon
                            variant="subtle"
                            size={44}
                            color="red"
                            aria-label="Disconnect Chromecast"
                            onClick={onDisconnect}
                        >
                            <ScreencastIcon size={26} weight="fill" />
                        </ActionIcon>
                    </Tooltip>
                )}

                <Popover
                    opened={settingsOpen}
                    onChange={onSettingsOpenChange}
                    position="top"
                    withArrow
                    shadow="md"
                    trapFocus
                >
                    <Popover.Target>
                        <Tooltip
                            label="Settings"
                            position="top"
                            disabled={settingsOpen}
                        >
                            <ActionIcon
                                variant="subtle"
                                size={44}
                                aria-label="Settings"
                                onClick={() =>
                                    onSettingsOpenChange(!settingsOpen)
                                }
                            >
                                <GearIcon size={26} weight="bold" />
                            </ActionIcon>
                        </Tooltip>
                    </Popover.Target>
                    <Popover.Dropdown
                        p="0.5rem"
                        style={{
                            width: 300,
                            backgroundColor: 'oklch(0.3 0 0 / 0.5)',
                            backdropFilter: 'blur(16px) saturate(1.5)',
                            boxShadow:
                                '0 0 0 1px transparent, 0 1px 3px 0 oklch(0 0 0 / 0.3), 0 1px 2px -1px oklch(0 0 0 / 0.3)',
                        }}
                    >
                        <PlayerSettings
                            {...settingsProps}
                            onClose={() => onSettingsOpenChange(false)}
                        />
                    </Popover.Dropdown>
                </Popover>
            </Group>
        </>
    )
}
