import { type ReactNode } from 'react'
import { PlayRequestSource } from '../../types/play-source.types'
import { AudioTrackLabel } from './audio-track-label'
import { OptionItem } from './option-item'
import { SettingsBody } from './settings-body'
import { SettingsGroupDivider } from './settings-group-divider'
import { SubMenuHeader } from './sub-menu-header'

export function AudioPanel({
    currentSource,
    audioLang,
    preferredAudioLangs,
    onAudioLangChange,
    back,
    onClose,
}: {
    currentSource: PlayRequestSource['source']
    audioLang: string | undefined
    preferredAudioLangs: string[] | undefined
    onAudioLangChange: (lang: string | undefined) => void
    back: () => void
    onClose?: () => void
}): ReactNode {
    const audioKey = (t: { language: string; index: number }) =>
        `${t.language}:${t.index}`
    const preferred = currentSource.audio.filter((t) =>
        preferredAudioLangs?.includes(t.language),
    )
    const other = currentSource.audio.filter(
        (t) => !preferredAudioLangs?.includes(t.language),
    )
    return (
        <>
            <SubMenuHeader title="Audio" onBack={back} />
            <SettingsBody>
                {preferred.map((track) => (
                    <OptionItem
                        key={track.index}
                        active={audioLang === audioKey(track)}
                        onClose={onClose}
                        onClick={() => {
                            onAudioLangChange(audioKey(track))
                            back()
                        }}
                    >
                        <AudioTrackLabel track={track} />
                    </OptionItem>
                ))}
                {preferred.length > 0 && other.length > 0 && (
                    <SettingsGroupDivider />
                )}
                {other.map((track) => (
                    <OptionItem
                        key={track.index}
                        active={audioLang === audioKey(track)}
                        onClose={onClose}
                        onClick={() => {
                            onAudioLangChange(audioKey(track))
                            back()
                        }}
                    >
                        <AudioTrackLabel track={track} />
                    </OptionItem>
                ))}
            </SettingsBody>
        </>
    )
}
