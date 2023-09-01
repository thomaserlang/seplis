import { Box, FormControl, FormLabel, Heading, Stack, Switch } from '@chakra-ui/react'
import { SelectGenre } from '@seplis/components/select-genre'
import { useForm } from 'react-hook-form'
import { SelectMovieUserSort } from './user-sort-select'
import { useEffect } from 'react'

export interface IUserFilterData {
    genre_id: number[]
    sort: string
    user_can_watch: boolean
}

export function MovieUserFilter({ defaultValue, onSubmit }: { defaultValue?: IUserFilterData, onSubmit?: (data: IUserFilterData) => void }) {
    const { register, handleSubmit, control, watch } = useForm<IUserFilterData>({
        defaultValues: defaultValue,
    })
    
    useEffect(() => {
        const sub = watch(() => handleSubmit(onSubmit)())
        return () => sub.unsubscribe()
    }, [onSubmit, watch])

    return <form onSubmit={handleSubmit(onSubmit)}>
        <Stack spacing="1rem">

            <FormControl display='flex' alignItems='center' justifyContent='space-between'>
                <FormLabel htmlFor='user-can-watch' alignItems='center' mb='0'>
                    Can watch
                </FormLabel>
                <Switch id='user-can-watch' {...register('user_can_watch')} size='lg' />
            </FormControl>

            <FormControl>
                <FormLabel htmlFor='sort'>Sort</FormLabel>
                <SelectMovieUserSort {...register('sort')} />
            </FormControl>
            
            <FormControl>
                <FormLabel htmlFor='genre'>Genre</FormLabel>
                <SelectGenre control={control} name="genre_id" />
            </FormControl>

        </Stack>
    </form>
}