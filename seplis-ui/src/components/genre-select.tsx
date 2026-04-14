import { useGetGenres } from '@/features/genres'
import { MediaType } from '@/features/media-type'
import {
    Button,
    Checkbox,
    Group,
    Popover,
    ScrollArea,
    Stack,
    TextInput,
} from '@mantine/core'
import { XIcon } from '@phosphor-icons/react'
import { useState } from 'react'

interface Props {
    type: MediaType
    selectedIds: number[]
    onSelected: (ids: number[]) => void
    children: React.ReactElement<{
        onClick: () => void
    }>
}

export function GenreSelect({
    type,
    selectedIds,
    onSelected,
    children,
}: Props) {
    const [search, setSearch] = useState('')
    const { data: genres } = useGetGenres({ params: { type } })

    if (!genres || genres.length === 0) return null

    const filtered = search
        ? genres.filter((g) =>
              g.name.toLowerCase().includes(search.toLowerCase()),
          )
        : genres

    function toggle(id: number) {
        const next = selectedIds.includes(id)
            ? selectedIds.filter((g) => g !== id)
            : [...selectedIds, id]
        onSelected(next)
    }

    return (
        <>
            <Popover
                position="bottom-start"
                shadow="md"
                withinPortal
                onClose={() => setSearch('')}
            >
                <Popover.Target>{children}</Popover.Target>
                <Popover.Dropdown p="xs">
                    <Group gap="xs" mb="xs" wrap="nowrap">
                        <TextInput
                            size="xs"
                            placeholder="Search genres..."
                            value={search}
                            onChange={(e) => setSearch(e.currentTarget.value)}
                            style={{ flex: 1 }}
                        />
                        {selectedIds.length > 0 && (
                            <Button
                                size="xs"
                                variant="subtle"
                                onClick={() => onSelected([])}
                                px={6}
                            >
                                <XIcon size={12} />
                            </Button>
                        )}
                    </Group>
                    <ScrollArea.Autosize mah={240}>
                        <Stack gap={6} pr="xs">
                            {filtered.map((genre) => (
                                <Checkbox
                                    key={genre.id}
                                    size="xs"
                                    label={genre.name}
                                    checked={selectedIds.includes(genre.id)}
                                    onChange={() => toggle(genre.id)}
                                />
                            ))}
                        </Stack>
                    </ScrollArea.Autosize>
                </Popover.Dropdown>
            </Popover>
        </>
    )
}
