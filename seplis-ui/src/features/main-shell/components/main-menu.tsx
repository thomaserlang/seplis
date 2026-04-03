import { MenuButton } from '@/components/menu-button'
import { mediaTypes } from '@/features/media-type'
import { SearchTrigger } from '@/features/search'
import { Button } from '@mantine/core'
import { MagnifyingGlassIcon } from '@phosphor-icons/react'
import { useSearchParams } from 'react-router-dom'

export function MainMenu() {
    const [_, setParams] = useSearchParams()
    return (
        <>
            <MenuButton label="Home" to="/" end />
            <MenuButton
                label="Series"
                to="/series"
                items={[{ label: 'All Series', to: '/series' }]}
            />
            <SearchTrigger
                onSelected={(item) => {
                    setParams((params) => {
                        params.set(
                            'mid',
                            `${mediaTypes[item.type].mediaType}-${item.id}`,
                        )
                        return params
                    })
                }}
            >
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
