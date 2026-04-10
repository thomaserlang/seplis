import { type ReactNode } from 'react'
import {
    PlayRequestSource,
    PlayRequestSources,
} from '../../types/play-source.types'
import { playSourceStr } from '../../utils/play-source.utils'
import { OptionItem } from './option-item'
import { SettingsBody } from './settings-body'
import { SubMenuHeader } from './sub-menu-header'

export function SourcePanel({
    playRequestsSources,
    currentRequest,
    currentSource,
    onSourceChange,
    back,
    onClose,
}: {
    playRequestsSources: PlayRequestSources[]
    currentRequest: PlayRequestSource['request']
    currentSource: PlayRequestSource['source']
    onSourceChange: (source: PlayRequestSource) => void
    back: () => void
    onClose?: () => void
}): ReactNode {
    return (
        <>
            <SubMenuHeader title="Source" onBack={back} />
            <SettingsBody>
                {playRequestsSources.map((server) =>
                    server.sources.map((src) => (
                        <OptionItem
                            key={`${server.request.play_id}-${src.index}`}
                            active={
                                currentRequest.play_id ===
                                    server.request.play_id &&
                                currentSource.index === src.index
                            }
                            onClose={onClose}
                            onClick={() => {
                                onSourceChange({
                                    request: server.request,
                                    source: src,
                                })
                                back()
                            }}
                        >
                            {playSourceStr(src)}
                        </OptionItem>
                    )),
                )}
            </SettingsBody>
        </>
    )
}
