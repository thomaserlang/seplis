import { Popover } from '@mantine/core'
import { GearIcon } from '@phosphor-icons/react'
import { ReactNode, useState } from 'react'
import { PlayerSettings, PlayerSettingsProps } from '../player-settings'
import { Button } from './button'

export interface SettingsPopoverProps extends PlayerSettingsProps {}

export function SettingsPopover(props: SettingsPopoverProps): ReactNode {
    const [open, setOpen] = useState(false)

    return (
        <Popover
            opened={open}
            onChange={setOpen}
            position="top"
            withinPortal={false}
            withArrow
            shadow="md"
            trapFocus
        >
            <Popover.Target>
                <Button
                    aria-label="Settings"
                    aria-expanded={open}
                    onClick={() => setOpen((value) => !value)}
                >
                    <GearIcon className="media-icon" weight="bold" />
                </Button>
            </Popover.Target>
            <Popover.Dropdown
                p="0.5rem"
                style={{
                    width: 300,
                    maxWidth: 'calc(100vw - 1rem)',
                    maxHeight: '80vh',
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                    backgroundColor: 'oklch(0.18 0 0 / 0.88)',
                    backdropFilter: 'blur(16px) saturate(1.5)',
                    boxShadow:
                        '0 0 0 1px transparent, 0 1px 3px 0 oklch(0 0 0 / 0.3), 0 1px 2px -1px oklch(0 0 0 / 0.3)',
                }}
            >
                <PlayerSettings {...props} onClose={() => setOpen(false)} />
            </Popover.Dropdown>
        </Popover>
    )
}
