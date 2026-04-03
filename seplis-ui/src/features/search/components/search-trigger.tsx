import { closeModal, openModal } from '@mantine/modals'
import React from 'react'
import { SearchResult } from '../types/search.types'
import { SearchView } from './search-view'

interface Props {
    onSelected?: (item: SearchResult) => void
    children: React.ReactElement<{ onClick: () => void }>
}

export function SearchTrigger({ children, onSelected }: Props) {
    return React.cloneElement(children, {
        onClick: () => {
            openModal({
                modalId: 'search-modal',
                title: 'Search',
                size: 'lg',
                children: (
                    <SearchView
                        onSelected={(item) => {
                            onSelected?.(item)
                            closeModal('search-modal')
                        }}
                    />
                ),
            })
        },
    })
}
