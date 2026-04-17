import { type ReactNode } from 'react'
import { PlayRequestSource } from '../../types/play-source.types'
import { languageMatch } from '../../utils/language-match'
import { trackLabel } from '../../utils/play-track.utils'
import { OptionItem } from './option-item'
import { SettingsBody } from './settings-body'
import { SettingsGroupDivider } from './settings-group-divider'
import { SubMenuHeader } from './sub-menu-header'

interface Props {
    currentSource: PlayRequestSource['source']
    activeSubtitleKey: string | undefined
    preferredSubtitleLangs: string[] | undefined
    onSubtitleChange: (key: string | undefined) => void
    back: () => void
    onClose?: () => void
}

export function SubtitlesPanel({
    currentSource,
    activeSubtitleKey,
    preferredSubtitleLangs,
    onSubtitleChange,
    back,
    onClose,
}: Props): ReactNode {
    const setSubtitle = (key: string | undefined) => {
        onSubtitleChange(key)
        back()
    }
    const preferred = currentSource.subtitles.filter((t) =>
        preferredSubtitleLangs
            ?.map((l) => languageMatch(t.language, l))
            .includes(true),
    )
    const other = currentSource.subtitles.filter(
        (t) =>
            !preferredSubtitleLangs
                ?.map((l) => languageMatch(t.language, l))
                .includes(true),
    )
    console.log(preferred)
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
