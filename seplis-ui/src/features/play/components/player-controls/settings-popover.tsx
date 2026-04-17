import { GearIcon } from '@phosphor-icons/react'
import { Popover } from '@videojs/react'
import { ReactNode, useState } from 'react'
import { PlayerSettings, PlayerSettingsProps } from '../player-settings'
import { Button } from './button'

export interface SettingsPopoverProps extends PlayerSettingsProps {}

export function SettingsPopover(props: SettingsPopoverProps): ReactNode {
    const [open, setOpen] = useState(false)

    const gearButton = (
        <Button aria-label="Settings">
            <GearIcon className="media-icon" weight="bold" />
        </Button>
    )

    return (
        <Popover.Root side="top" open={open} onOpenChange={setOpen}>
            <Popover.Trigger render={gearButton} />
            <Popover.Popup className="media-surface media-popover media-popover--settings">
                <PlayerSettings {...props} onClose={() => setOpen(false)} />
            </Popover.Popup>
        </Popover.Root>
    )
}
