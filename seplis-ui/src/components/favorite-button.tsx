import { Button, ButtonProps } from '@mantine/core'
import { StarIcon } from '@phosphor-icons/react'

interface Props extends ButtonProps {
    active: boolean
    onClick?: () => void
}

export function FavoriteButton({ active, ...props }: Props) {
    return (
        <Button
            color={active ? '#90cdf4' : 'var(--secondary)'}
            variant="filled"
            autoContrast={true}
            size="compact-md"
            leftSection={<StarIcon weight="fill" />}
            {...props}
        >
            Favorite
        </Button>
    )
}
