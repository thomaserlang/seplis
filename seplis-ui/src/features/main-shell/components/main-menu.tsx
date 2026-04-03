import { MenuButton } from '@/components/menu-button/menu-button'
import { SearchTrigger } from '@/features/search/components/search-trigger'
import { Button } from '@mantine/core'
import { MagnifyingGlassIcon } from '@phosphor-icons/react'
import { useNavigate } from 'react-router-dom'

export function MainMenu() {
    const navigate = useNavigate()
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
                    console.log(item)
                    switch (item.type) {
                        case 'series': {
                            navigate(`/series/${item.id}`)
                            break
                        }
                        case 'movie': {
                            navigate(`/movies/${item.id}`)
                            break
                        }
                    }
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
