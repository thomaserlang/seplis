import { GearIcon } from '@phosphor-icons/react'
import { Popover } from '@videojs/react'
import { ComponentProps, ReactNode } from 'react'
import { PlayerSettings, PlayerSettingsProps } from '../player-settings'
import { Button } from './button'

export interface SettingsPopoverProps extends PlayerSettingsProps {}

export function SettingsPopover(props: SettingsPopoverProps): ReactNode {
    return (
        <Popover.Root side="top" delay={200} closeDelay={100}>
            <Popover.Trigger render={<SettingsButton />} />
            <Popover.Popup className="media-surface media-popover media-popover--settings">
                <PlayerSettings {...props} />
            </Popover.Popup>
        </Popover.Root>
    )
}

function SettingsButton(props: ComponentProps<'button'>) {
    return (
        <Button className="media-button--settings" {...props}>
            <GearIcon className="media-icon media-icon--settings" />
        </Button>
    )
}
