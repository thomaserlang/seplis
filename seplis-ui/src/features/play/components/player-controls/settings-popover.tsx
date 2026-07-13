import { Popover } from '@mantine/core'
import { GearIcon } from '@phosphor-icons/react'
import { ReactNode } from 'react'
import { PlayerSettings, PlayerSettingsProps } from '../player-settings'
import { Button } from './button'

export interface SettingsPopoverProps extends PlayerSettingsProps {
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function SettingsPopover({
    open,
    onOpenChange,
    ...props
}: SettingsPopoverProps): ReactNode {
    return (
        <Popover
            opened={open}
            onChange={onOpenChange}
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
                    onClick={() => onOpenChange(!open)}
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
                <PlayerSettings
                    {...props}
                    onClose={() => onOpenChange(false)}
                />
            </Popover.Dropdown>
        </Popover>
    )
}
