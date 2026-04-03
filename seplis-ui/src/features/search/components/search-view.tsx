import { Flex, TextInput } from '@mantine/core'
import { useField } from '@mantine/form'
import { SearchResults } from './search-results'

interface Props {}

export function SearchView({}: Props) {
    const field = useField({
        mode: 'controlled',
        initialValue: '',
    })

    return (
        <Flex direction="column" gap="1rem">
            <TextInput
                placeholder="Search..."
                size="lg"
                data-autofocus
                {...field.getInputProps()}
            />

            <SearchResults query={field.getValue()} />
        </Flex>
    )
}
