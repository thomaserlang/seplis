import { FormControl, FormLabel, Stack, Switch } from '@chakra-ui/react'
import { SelectGenre } from '@seplis/components/select-genre'
import { useForm } from 'react-hook-form'
import { SelectSeriesUserSort } from './user-sort-select'
import { useEffect } from 'react'

export interface IUserFilterData {
    genre_id?: number[]
    sort?: string | null
    user_can_watch?: boolean | null
    premiered_gt?: string | null
    premiered_lt?: string | null
}

export function SeriesUserFilter({ defaultValue, onSubmit }: { defaultValue?: IUserFilterData, onSubmit?: (data: IUserFilterData) => void }) {
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
                <SelectSeriesUserSort {...register('sort')} />
            </FormControl>
            
            <Stack spacing="0.25rem">
                <FormControl display='flex' alignItems='center' justifyContent='space-between' mb='0'>
                    <FormLabel alignItems='center' mb='0'>
                        Premiered
                    </FormLabel>                
                </FormControl>

                <FormControl display='flex' alignItems='center' justifyContent='space-between'>
                    <FormLabel htmlFor='premiered_gt' alignItems='center' mb='0' fontWeight='normal'>
                        From:
                    </FormLabel>
                    <input id='premiered_gt' type='date' {...register('premiered_gt')} />
                </FormControl>

                <FormControl display='flex' alignItems='center' justifyContent='space-between'>
                    <FormLabel htmlFor='premiered_lt' alignItems='center' mb='0' fontWeight='normal'>
                        To:
                    </FormLabel>
                    <input id='premiered_lt' type='date' {...register('premiered_lt')} />
                </FormControl>
            </Stack>

            <FormControl>
                <FormLabel htmlFor='genres'>Genres</FormLabel>
                <SelectGenre control={control} name='genre_id' type='series' />
            </FormControl>

        </Stack>
    </form>
}