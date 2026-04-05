import { Button, ButtonProps } from '@mantine/core'
import { StarIcon } from '@phosphor-icons/react'

interface Props extends ButtonProps {
    active: boolean
    onClick?: () => void
}

export function FavoriteButton({ active, ...props }: Props) {
    return (
        <Button
            style={
                active
                    ? ({
                          '--favorite': 'oklch(0.55 0.18 55)',
                          '--button-bg': 'var(--favorite)',
                          '--button-hover':
                              'color-mix(in oklab, var(--favorite) 95%, white)',
                          '--button-active': 'var(--favorite)',
                          '--button-bd':
                              '0.0625rem solid color-mix(in oklab, var(--favorite) 80%, white)',
                      } as React.CSSProperties)
                    : undefined
            }
            variant="default"
            size="compact-md"
            leftSection={<StarIcon weight={active ? 'fill' : 'regular'} />}
            {...props}
        >
            Favorite
        </Button>
    )
}
