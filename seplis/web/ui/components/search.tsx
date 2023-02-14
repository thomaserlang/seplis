import { SearchIcon } from '@chakra-ui/icons'
import { Text, Button, Input, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, useDisclosure, FormControl, FormLabel, Switch, Box, AspectRatio, Skeleton, Heading, Tag, Stack } from '@chakra-ui/react'
import api from '@seplis/api'
import { ITitleSearchResult as ISearchTitleResult } from '@seplis/interfaces/search'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { useDebounce } from 'usehooks-ts'
import { Poster } from './poster'


export function SearchButtonDialog() {
    const { isOpen, onOpen, onClose } = useDisclosure()
    return (
        <>
            <Button leftIcon={<SearchIcon />} onClick={onOpen}>Search</Button>

            <Modal isOpen={isOpen} onClose={onClose}>
                <ModalOverlay />
                <ModalContent backgroundColor="gray.900" maxWidth="800px" paddingBottom="1rem">
                    <ModalHeader>Search</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <Search afterSelected={onClose} />
                    </ModalBody>
                </ModalContent>
            </Modal>
        </>
    )
}

export function Search({ afterSelected }: { afterSelected?: (item: ISearchTitleResult) => void }) {
    const [value, setValue] = useState('')
    const query = useDebounce(value, 200)
    const navigate = useNavigate()
    const { data, isFetching } = useQuery(['search-suggestions', query], async ({ signal }) => {
        const r = await api.get<ISearchTitleResult[]>('/2/search', {
            params: {
                'query': query,
            },
            signal: signal,
        })
        return r.data
    }, {
        enabled: query.length > 0,
        keepPreviousData: false,
    })

    return <Stack direction="column">
        <SearchInput onChange={setValue} />

        { isFetching && <RenderItemSkeleton />}

        {!isFetching && <RenderItems items={data} onSelected={(item) => {
            if (item.type == 'movie')
                navigate(`/${item.type}s/${item.id}`)
            else if (item.type == 'series')
                navigate(`/series/${item.id}`)
            if (afterSelected)
                afterSelected(item)
        }} />}
    </Stack>
}


function RenderItems({ items, onSelected }: { items: ISearchTitleResult[], onSelected: (item: ISearchTitleResult) => void }) {
    if (!items)
        return null
    if (items.length === 0)
        return <Heading as="h2" fontSize="1.25rem" fontWeight="600">No results</Heading>
    return <Stack direction="column">
        {items.map(item => (
            <RenderItem key={`${item.type}-${item.id}`} item={item} onSelected={onSelected} />
        ))}
    </Stack>
}

function RenderItem({ item, onSelected }: { item: ISearchTitleResult, onSelected: (item: ISearchTitleResult) => void }) {
    return <Stack
        direction="row"
        backgroundColor="blackAlpha.500"
        padding="0.5rem"
        rounded="md"
        cursor="pointer"
        onClick={() => {
            onSelected(item)
        }}
    >
        <AspectRatio width="15%" ratio={603 / 887} rounded="sm" overflow="hidden">
            <Poster url={`${item.poster_image?.url}@SX320.webp`} title={item.title} />
        </AspectRatio>
        <Stack direction="column" lineHeight="1.3" spacing="0.25rem">
            <Text fontWeight="600">{item.title}</Text>
            {item.release_date ? <Text>{item.release_date.substring(0,4)}</Text> : null}
            <Stack direction="row"><ShowType type={item.type} /></Stack>
        </Stack>
    </Stack>
}


function ShowType({ type }: { type: string }) {
    if (type === 'movie')
        return <Tag colorScheme="green">Movie</Tag>
    else if (type === 'series')
        return <Tag colorScheme="blue">Series</Tag>
    return null
}


function RenderItemSkeleton() {
    return <Stack
        direction="row"
        backgroundColor="blackAlpha.500"
        padding="0.5rem"
        rounded="md"
    >
        <AspectRatio width="15%" ratio={603 / 887} rounded="sm" overflow="hidden">
            <Skeleton height="100%" />
        </AspectRatio>
        <Stack width="100%">
            <Skeleton height="30px" width="45%" />
            <Skeleton height="30px" width="27%" />
        </Stack>
    </Stack>
}


function SearchInput({ onChange }: { onChange: (value: string) => void }) {
    const { register, setFocus } = useForm()
    useEffect(() => {
        setFocus('query')
    })
    return <form>
        <Input
            {...register('query')}
            onChange={(e) => onChange(e.currentTarget.value)}
            type="text"
            placeholder="Search title" size="lg"
        />
    </form>
}