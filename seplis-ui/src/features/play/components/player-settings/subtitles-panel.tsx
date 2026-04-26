import { type ReactNode } from 'react'
import {
    PlayRequestSource,
    PlaySourceStream,
} from '../../types/play-source.types'
import { languageMatch } from '../../utils/language-match'
import { toLangKey } from '../../utils/play-source.utils'
import { trackLabel } from '../../utils/play-track.utils'
import { OptionItem } from './option-item'
import { SettingsBody } from './settings-body'
import { SettingsGroupDivider } from './settings-group-divider'
import { SubMenuHeader } from './sub-menu-header'

interface Props {
    currentSource: PlayRequestSource['source']
    subtitle: PlaySourceStream | undefined
    preferredSubtitleLangs: string[] | undefined
    onSubtitleChange: (source: PlaySourceStream | undefined) => void
    back: () => void
    onClose?: () => void
}

export function SubtitlesPanel({
    currentSource,
    subtitle,
    preferredSubtitleLangs,
    onSubtitleChange,
    back,
    onClose,
}: Props): ReactNode {
    const setSubtitle = (source: PlaySourceStream | undefined) => {
        onSubtitleChange(source)
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

    return (
        <>
            <SubMenuHeader title="Subtitles" onBack={back} />
            <SettingsBody>
                <OptionItem
                    active={!subtitle}
                    onClose={onClose}
                    onClick={() => setSubtitle(undefined)}
                >
                    Off
                </OptionItem>
                {preferred.map((source) => {
                    const key = toLangKey(source)
                    return (
                        <OptionItem
                            key={key}
                            active={
                                subtitle?.group_index === source.group_index
                            }
                            onClose={onClose}
                            onClick={() => setSubtitle(source)}
                        >
                            {trackLabel(source.title, source.language)}
                            {source.forced && ' (Forced)'}
                        </OptionItem>
                    )
                })}
                {preferred.length > 0 && other.length > 0 && (
                    <SettingsGroupDivider />
                )}
                {other.map((source) => {
                    const key = toLangKey(source)
                    return (
                        <OptionItem
                            key={key}
                            active={
                                subtitle?.group_index === source.group_index
                            }
                            onClose={onClose}
                            onClick={() => setSubtitle(source)}
                        >
                            {trackLabel(source.title, source.language)}
                            {source.forced && ' (Forced)'}
                        </OptionItem>
                    )
                })}
            </SettingsBody>
        </>
    )
}
