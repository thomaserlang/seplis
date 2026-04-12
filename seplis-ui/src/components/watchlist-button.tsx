import { Button, ButtonProps, ButtonSize } from '@mantine/core'
import { BookmarkSimpleIcon } from '@phosphor-icons/react'

export interface WatchlistButtonProps extends ButtonProps {
    active?: boolean
    onClick?: () => void
    size?: ButtonSize
}

export function WatchlistButton({ active, ...props }: WatchlistButtonProps) {
    return (
        <Button
            style={
                active
                    ? ({
                          '--watchlist': 'oklch(0.45 0.18 280)',
                          '--button-bg': 'var(--watchlist)',
                          '--button-hover':
                              'color-mix(in oklab, var(--watchlist) 95%, white)',
                          '--button-active': 'var(--watchlist)',
                          '--button-bd':
                              '0.0625rem solid color-mix(in oklab, var(--watchlist) 80%, white)',
                      } as React.CSSProperties)
                    : undefined
            }
            variant="default"
            size="compact-md"
            leftSection={
                <BookmarkSimpleIcon weight={active ? 'fill' : 'regular'} />
            }
            {...props}
        >
            Watchlist
        </Button>
    )
}
