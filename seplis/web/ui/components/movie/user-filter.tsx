import { Box, Button, Heading, Stack } from '@chakra-ui/react'
import { SelectGenre } from '@seplis/components/select-genre'
import { useForm } from 'react-hook-form'
import { SelectMovieUserSort } from './user-sort-select'

interface IUserFilterData {
    genre_id: number
    sort: string
}

export function MovieUserFilter({ defaultValue, onSubmit }: { defaultValue?: IUserFilterData, onSubmit?: (data: IUserFilterData) => void }) {
    const { register, handleSubmit } = useForm<IUserFilterData>({
        defaultValues: defaultValue,
    })

    return <form onSubmit={handleSubmit(onSubmit)}>
        <Stack spacing="1rem">
            <Box>
                <Heading fontSize="16px" fontWeight="600" marginBottom="0.25rem">Genre</Heading>
                <SelectGenre {...register('genre_id')} />
            </Box>

            <Box marginBottom="0.25rem">
                <Heading fontSize="16px" fontWeight="600" marginBottom="0.25rem">Sort</Heading>
                <SelectMovieUserSort {...register('sort')} />
            </Box>

            <Button type="submit" colorScheme="blue">Apply filter</Button>
        </Stack>
    </form>
}