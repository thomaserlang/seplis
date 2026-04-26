import { type ReactNode } from 'react'
import {
    PlayRequestSource,
    PlaySourceStream,
} from '../../types/play-source.types'
import { languageMatch } from '../../utils/language-match'
import { AudioLabel } from './audio-label'
import { OptionItem } from './option-item'
import { SettingsBody } from './settings-body'
import { SettingsGroupDivider } from './settings-group-divider'
import { SubMenuHeader } from './sub-menu-header'

interface Props {
    currentSource: PlayRequestSource['source']
    audio: PlaySourceStream | undefined
    preferredAudioLangs: string[] | undefined
    onAudioChange: (source: PlaySourceStream | undefined) => void
    back: () => void
    onClose?: () => void
}

export function AudioPanel({
    currentSource,
    audio,
    preferredAudioLangs,
    onAudioChange,
    back,
    onClose,
}: Props): ReactNode {
    const preferred = currentSource.audio.filter((t) =>
        preferredAudioLangs
            ?.map((l) => languageMatch(t.language, l))
            .includes(true),
    )
    const other = currentSource.audio.filter(
        (t) =>
            !preferredAudioLangs
                ?.map((l) => languageMatch(t.language, l))
                .includes(true),
    )
    return (
        <>
            <SubMenuHeader title="Audio" onBack={back} />
            <SettingsBody>
                {preferred.map((source) => (
                    <OptionItem
                        key={source.index}
                        active={audio?.group_index === source.group_index}
                        onClose={onClose}
                        onClick={() => {
                            onAudioChange(source)
                            back()
                        }}
                    >
                        <AudioLabel source={source} />
                    </OptionItem>
                ))}
                {preferred.length > 0 && other.length > 0 && (
                    <SettingsGroupDivider />
                )}
                {other.map((source) => (
                    <OptionItem
                        key={source.index}
                        active={audio?.group_index === source.group_index}
                        onClose={onClose}
                        onClick={() => {
                            onAudioChange(source)
                            back()
                        }}
                    >
                        <AudioLabel source={source} />
                    </OptionItem>
                ))}
            </SettingsBody>
        </>
    )
}
