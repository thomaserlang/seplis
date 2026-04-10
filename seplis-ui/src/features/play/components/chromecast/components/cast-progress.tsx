import { Group, Slider, Stack, Text } from '@mantine/core'
import type { ReactNode } from 'react'

interface Props {
    currentTime: number
    duration: number
    canSeek: boolean
    onDragChange: (value: number) => void
    onSeek: (value: number) => void
    formatTime: (secs: number) => string
}

export function CastProgress({
    currentTime,
    duration,
    canSeek,
    onDragChange,
    onSeek,
    formatTime,
}: Props): ReactNode {
    return (
        <Stack gap={6} style={{ width: '100%', maxWidth: 400 }}>
            <Slider
                value={currentTime}
                min={0}
                max={duration || 1}
                step={1}
                onChange={onDragChange}
                onChangeEnd={onSeek}
                disabled={!canSeek}
                size="sm"
                label={null}
                styles={{ thumb: { transition: 'none' } }}
            />
            <Group justify="space-between">
                <Text size="xs" ff="monospace" c="dimmed">
                    {formatTime(currentTime)}
                </Text>
                <Text size="xs" ff="monospace" c="dimmed">
                    {formatTime(duration)}
                </Text>
            </Group>
        </Stack>
    )
}
