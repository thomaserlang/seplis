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
    selected: string[]
    onChange: (ids: string[]) => void
    children: React.ReactElement<{
        onClick: () => void
    }>
}

export function LanguageSelect({ selected, onChange, children }: Props) {
    const [search, setSearch] = useState('')
    const languages = ALL_LANGUAGES

    const filtered = search
        ? languages.filter((g) =>
              g.name.toLowerCase().includes(search.toLowerCase()),
          )
        : languages

    function toggle(lang: string) {
        const next = selected.includes(lang)
            ? selected.filter((g) => g !== lang)
            : [...selected, lang]
        onChange(next)
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
                            placeholder="Search language"
                            value={search}
                            onChange={(e) => setSearch(e.currentTarget.value)}
                            style={{ flex: 1 }}
                        />
                        {selected.length > 0 && (
                            <Button
                                size="xs"
                                variant="subtle"
                                onClick={() => onChange([])}
                                px={6}
                            >
                                <XIcon size={12} />
                            </Button>
                        )}
                    </Group>
                    <ScrollArea.Autosize mah={240}>
                        <Stack gap={6} pr="xs">
                            {filtered.map((lang) => (
                                <Checkbox
                                    key={lang.code}
                                    size="xs"
                                    label={lang.name}
                                    checked={selected.includes(lang.code)}
                                    onChange={() => toggle(lang.code)}
                                />
                            ))}
                        </Stack>
                    </ScrollArea.Autosize>
                </Popover.Dropdown>
            </Popover>
        </>
    )
}

const displayNames = new Intl.DisplayNames(['en'], { type: 'language' })
const ALL_LANGUAGES: { code: string; name: string }[] =
    Intl.getCanonicalLocales(
        // BCP 47 two-letter language subtags (ISO 639-1)
        // prettier-ignore
        [
            'en', 'ja', 'da', 'sv', 'no', 'es', 'fr', 'de', 
        ],
    )
        .map((code) => {
            try {
                const name = displayNames.of(code)
                return name ? { code, name } : null
            } catch {
                return null
            }
        })
        .filter((l): l is { code: string; name: string } => l !== null)
