import { type ReactNode } from 'react'
import { PlayRequestSource } from '../../types/play-source.types'
import { trackLabel } from './audio-track-label'
import { OptionItem } from './option-item'
import { SettingsBody } from './settings-body'
import { SettingsGroupDivider } from './settings-group-divider'
import { SubMenuHeader } from './sub-menu-header'

export function SubtitlesPanel({
    currentSource,
    activeSubtitleKey,
    preferredSubtitleLangs,
    onSubtitleChange,
    back,
    onClose,
}: {
    currentSource: PlayRequestSource['source']
    activeSubtitleKey: string | undefined
    preferredSubtitleLangs: string[] | undefined
    onSubtitleChange: (key: string | undefined) => void
    back: () => void
    onClose?: () => void
}): ReactNode {
    const setSubtitle = (key: string | undefined) => {
        onSubtitleChange(key)
        back()
    }
    const preferred = currentSource.subtitles.filter((t) =>
        preferredSubtitleLangs?.includes(t.language),
    )
    const other = currentSource.subtitles.filter(
        (t) => !preferredSubtitleLangs?.includes(t.language),
    )
    return (
        <>
            <SubMenuHeader title="Subtitles" onBack={back} />
            <SettingsBody>
                <OptionItem
                    active={!activeSubtitleKey}
                    onClose={onClose}
                    onClick={() => setSubtitle(undefined)}
                >
                    Off
                </OptionItem>
                {preferred.map((track) => {
                    const key = `${track.language}:${track.index}`
                    return (
                        <OptionItem
                            key={key}
                            active={activeSubtitleKey === key}
                            onClose={onClose}
                            onClick={() => setSubtitle(key)}
                        >
                            {trackLabel(track.title, track.language)}
                            {track.forced && ' (Forced)'}
                        </OptionItem>
                    )
                })}
                {preferred.length > 0 && other.length > 0 && (
                    <SettingsGroupDivider />
                )}
                {other.map((track) => {
                    const key = `${track.language}:${track.index}`
                    return (
                        <OptionItem
                            key={key}
                            active={activeSubtitleKey === key}
                            onClose={onClose}
                            onClick={() => setSubtitle(key)}
                        >
                            {trackLabel(track.title, track.language)}
                            {track.forced && ' (Forced)'}
                        </OptionItem>
                    )
                })}
            </SettingsBody>
        </>
    )
}
