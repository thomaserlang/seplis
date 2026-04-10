import { type ReactNode } from 'react'
import { MAX_BITRATE } from '../../constants/play-bitrate.constants'
import { PlayRequestSource } from '../../types/play-source.types'
import {
    bitratePretty,
    playSourceBitrateStr,
} from '../../utils/play-bitrate.utils'
import { OptionItem } from './option-item'
import { SettingsBody } from './settings-body'
import { SubMenuHeader } from './sub-menu-header'

export function BitratePanel({
    availableBitrates,
    maxBitrate,
    currentSource,
    onBitrateChange,
    back,
    onClose,
}: {
    availableBitrates: number[]
    maxBitrate: number
    currentSource: PlayRequestSource['source']
    onBitrateChange: (bitrate: number) => void
    back: () => void
    onClose?: () => void
}): ReactNode {
    return (
        <>
            <SubMenuHeader title="Quality" onBack={back} />
            <SettingsBody>
                {availableBitrates.map((bitrate) => (
                    <OptionItem
                        key={bitrate}
                        active={maxBitrate === bitrate}
                        onClose={onClose}
                        onClick={() => {
                            onBitrateChange(bitrate)
                            back()
                        }}
                    >
                        {bitrate === MAX_BITRATE ||
                        bitrate >= currentSource.bit_rate
                            ? `Max (${bitratePretty(currentSource.bit_rate)})`
                            : playSourceBitrateStr(bitrate, currentSource)}
                    </OptionItem>
                ))}
            </SettingsBody>
        </>
    )
}
