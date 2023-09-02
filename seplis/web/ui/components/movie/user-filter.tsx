import { Box, FormControl, FormLabel, Heading, Stack, Switch } from '@chakra-ui/react'
import { SelectGenre } from '@seplis/components/select-genre'
import { useForm } from 'react-hook-form'
import { SelectMovieUserSort } from './user-sort-select'
import { useEffect } from 'react'

export interface IUserFilterData {
    genre_id: number[]
    sort: string
    user_can_watch: boolean
    release_date_gt: string
    release_date_lt: string
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
            
            <Stack spacing="0.25rem">
                <FormControl display='flex' alignItems='center' justifyContent='space-between' mb='0'>
                    <FormLabel alignItems='center' mb='0'>
                        Release date
                    </FormLabel>                
                </FormControl>

                <FormControl display='flex' alignItems='center' justifyContent='space-between'>
                    <FormLabel htmlFor='release_date_gt' alignItems='center' mb='0' fontWeight='normal'>
                        From:
                    </FormLabel>
                    <input id='release_date_gt' type='date' {...register('release_date_gt')} />
                </FormControl>

                <FormControl display='flex' alignItems='center' justifyContent='space-between'>
                    <FormLabel htmlFor='release_date_lt' alignItems='center' mb='0' fontWeight='normal'>
                        To:
                    </FormLabel>
                    <input id='release_date_lt' type='date' {...register('release_date_lt')} />
                </FormControl>
            </Stack>
            
            <FormControl>
                <FormLabel>Genres</FormLabel>
                <SelectGenre control={control} name='genre_id' type='movie' />
            </FormControl>

        </Stack>
    </form>
}