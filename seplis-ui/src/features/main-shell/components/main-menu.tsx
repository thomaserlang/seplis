import { MenuButton } from '@/components/menu-button/menu-button'
import { SearchTrigger } from '@/features/search/components/search-trigger'
import { Button } from '@mantine/core'
import { MagnifyingGlassIcon } from '@phosphor-icons/react'

export function MainMenu() {
    return (
        <>
            <MenuButton label="Home" to="/" end />
            <MenuButton
                label="Series"
                to="/series"
                items={[{ label: 'All Series', to: '/series' }]}
            />
            <SearchTrigger>
                <Button
                    size="compact-md"
                    variant="subtle"
                    leftSection={<MagnifyingGlassIcon weight="bold" />}
                >
                    Search
                </Button>
            </SearchTrigger>
        </>
    )
}
