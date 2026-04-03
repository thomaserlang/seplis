import { openModal } from '@mantine/modals'
import React from 'react'
import { SearchView } from './search-view'

interface Props {
    children: React.ReactElement<{ onClick: () => void }>
}

export function SearchTrigger({ children }: Props) {
    return React.cloneElement(children, {
        onClick: () => {
            openModal({
                title: 'Search',
                size: 'lg',
                children: <SearchView />,
            })
        },
    })
}
