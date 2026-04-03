import { Button, ButtonProps } from '@mantine/core'
import { BookmarkSimpleIcon } from '@phosphor-icons/react'

interface Props extends ButtonProps {
    active: boolean
    onClick?: () => void
}

export function WatchlistButton({ active, ...props }: Props) {
    return (
        <Button
            color={active ? '#FAF089' : 'var(--secondary)'}
            variant="filled"
            autoContrast={true}
            size="compact-md"
            leftSection={<BookmarkSimpleIcon weight="fill" />}
            {...props}
        >
            Watchlist
        </Button>
    )
}
