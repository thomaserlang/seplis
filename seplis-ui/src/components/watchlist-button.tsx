import { Button, ButtonProps } from '@mantine/core'
import { BookmarkSimpleIcon } from '@phosphor-icons/react'

interface Props extends ButtonProps {
    active: boolean
    onClick?: () => void
}

export function WatchlistButton({ active, ...props }: Props) {
    return (
        <Button
            style={
                active
                    ? ({
                          '--watchlist': 'oklab(50% 0.1 0.1 / 0.5)',
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
