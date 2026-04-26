import { Flex, Text } from '@mantine/core'
import { type ReactNode } from 'react'
import type {
    PlaybackTransport,
    TranscodeDecision,
} from '../../../types/transcode-decision.types'
import { SettingsBody } from '../settings-body'
import { SubMenuHeader } from '../sub-menu-header'
import {
    decisionReasons,
    streamSummary,
    transportLabel,
} from './transcode-decision-formatters'
import { transcodeDecisionLabel } from './transcode-decision-label'

interface Props {
    transcodeDecision: TranscodeDecision
    playbackTransport?: PlaybackTransport
    back: () => void
}

export function TranscodeDecisionPanel({
    transcodeDecision,
    playbackTransport,
    back,
}: Props): ReactNode {
    const reasons = decisionReasons(transcodeDecision, playbackTransport)

    return (
        <>
            <SubMenuHeader title="Playback Decision" onBack={back} />
            <SettingsBody mah="22rem">
                <Flex
                    direction="column"
                    px="0.75rem"
                    pt="0.55rem"
                    pb="0.65rem"
                    style={{
                        borderBottom:
                            '1px solid color-mix(in srgb, currentColor 15%, transparent)',
                    }}
                >
                    <Text fw={700} lh={1.2}>
                        {transcodeDecisionLabel(
                            transcodeDecision,
                            playbackTransport,
                        )}
                    </Text>
                </Flex>
                {reasons.length > 0 && (
                    <Flex direction="column" px="0.75rem" py="0.55rem">
                        <Text fw={600} fz="0.85rem">
                            Why
                        </Text>
                        <Flex
                            direction="column"
                            gap="0.25rem"
                            mt="0.25rem"
                            fz="0.9rem"
                            lh={1.35}
                            opacity={0.72}
                        >
                            {reasons.map((reason, index) => (
                                <Text key={`${reason}-${index}`} inherit>
                                    {reason}
                                </Text>
                            ))}
                        </Flex>
                    </Flex>
                )}
                <Flex
                    direction="column"
                    px="0.75rem"
                    py="0.35rem"
                    style={{
                        borderTop:
                            '1px solid color-mix(in srgb, currentColor 10%, transparent)',
                    }}
                >
                    <DecisionRow
                        label="Delivery"
                        value={transportLabel(
                            playbackTransport,
                            transcodeDecision,
                        )}
                    />
                    <DecisionRow
                        label="Video"
                        value={streamSummary(transcodeDecision.video)}
                        tone={transcodeDecision.video.action}
                    />
                    <DecisionRow
                        label="Audio"
                        value={streamSummary(transcodeDecision.audio)}
                        tone={transcodeDecision.audio.action}
                    />
                </Flex>
            </SettingsBody>
        </>
    )
}

function DecisionRow({
    label,
    value,
    tone,
}: {
    label: string
    value: string
    tone?: 'copy' | 'transcode'
}): ReactNode {
    return (
        <Flex
            align="center"
            justify="space-between"
            gap="0.5rem"
            py="0.22rem"
        >
            <Text fw={500} opacity={0.65}>{label}</Text>
            <Text
                fw={600}
                ta="right"
                style={{
                    minWidth: 0,
                    overflowWrap: 'anywhere',
                    color: decisionRowColor(tone),
                }}
            >
                {value}
            </Text>
        </Flex>
    )
}

function decisionRowColor(tone: 'copy' | 'transcode' | undefined) {
    if (tone === 'copy') return 'color-mix(in srgb, #2dd36f 80%, white)'
    if (tone === 'transcode') return 'color-mix(in srgb, #ffb020 86%, white)'

    return undefined
}
