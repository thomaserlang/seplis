import { FormControl, FormLabel, Heading, Input, Select, Stack, Switch } from '@chakra-ui/react'
import { SelectGenre } from '@seplis/components/select-genre'
import { useForm } from 'react-hook-form'
import { SelectMovieUserSort } from './user-sort-select'
import { useEffect } from 'react'
import { SelectLanguage } from '../select-language'
import { SwitchRadioGroup } from '../switch-radio-group'

export interface IUserFilterData {
    genre_id?: number[]
    sort?: string | null
    user_can_watch?: boolean | null
    release_date_gt?: string | null
    release_date_lt?: string | null
    rating_gt?: number | null
    rating_lt?: number | null
    rating_votes_gt?: number | null
    language?: string | null
    user_has_watched?: string | null
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
            
            <FormControl>
                <FormLabel htmlFor='sort' color='blue.300'>Sort by</FormLabel>
                <SelectMovieUserSort {...register('sort')} />
            </FormControl>

            <FormControl display='flex' alignItems='center' justifyContent='space-between'>
                <FormLabel htmlFor='user-can-watch' alignItems='center' mb='0' color='blue.300'>
                    On play servers
                </FormLabel>
                <Switch id='user-can-watch' {...register('user_can_watch')} size='lg' />
            </FormControl>

            <SwitchRadioGroup control={control} name='user_has_watched' options={[
                { name: 'Have watched', value: 'true' },
                { name: 'Have NOT watched', value: 'false' },
            ]} />
            
            <Stack spacing="0.25rem">
                <FormControl display='flex' alignItems='center' justifyContent='space-between' mb='0'>
                    <FormLabel alignItems='center' mb='0' color='blue.300'>
                        Release date
                    </FormLabel>                
                </FormControl>
                <FormControl display='flex' alignItems='center' justifyContent='space-between'>
                    <FormLabel htmlFor='release_date_gt' alignItems='center' mb='0' fontWeight='normal'>
                        From:
                    </FormLabel>
                    <Input id='release_date_gt' type='date' {...register('release_date_gt')} width='auto' />
                </FormControl>
                <FormControl display='flex' alignItems='center' justifyContent='space-between'>
                    <FormLabel htmlFor='release_date_lt' alignItems='center' mb='0' fontWeight='normal'>
                        To:
                    </FormLabel>
                    <Input id='release_date_lt' type='date' {...register('release_date_lt')} width='auto' />
                </FormControl>
            </Stack>
            
            <Stack spacing="0.25rem">
                <FormControl display='flex' alignItems='center' justifyContent='space-between' mb='0'>
                    <FormLabel alignItems='center' mb='0' color='blue.300'>
                        Rating
                    </FormLabel>
                </FormControl>
                <FormControl display='flex' alignItems='center' justifyContent='space-between'>
                    <FormLabel htmlFor='rating_gt' alignItems='center' mb='0' fontWeight='normal'>
                        From:
                    </FormLabel>
                    <Select id='rating_gt' {...register('rating_gt')} width='auto'>
                        {[...Array(11).keys()].map((i) => (
                            <option key={i} value={i}>{i}</option>
                        ))}
                    </Select>
                    <FormLabel htmlFor='rating_lt' alignItems='center' mb='0' fontWeight='normal'>
                        To:
                    </FormLabel>
                    <Select id='rating_lt' {...register('rating_lt')} width='auto' defaultValue={10}>
                        {[...Array(10).keys()].map((i) => (
                            <option key={i+1} value={i+1}>{i+1}</option>
                        ))}
                    </Select>
                </FormControl>
                <FormControl display='flex' alignItems='center' justifyContent='space-between'>
                    <FormLabel htmlFor='rating_gt' alignItems='center' mb='0' fontWeight='normal'>
                        Minumum votes:
                    </FormLabel>
                    <Select id='rating_lt' {...register('rating_votes_gt')} width='auto'>
                        {[...Array(31).keys()].map((i) => (
                            <option key={i} value={i*100}>{i*100}</option>
                        ))}
                    </Select>
                </FormControl>
            </Stack>
            
            <FormControl>
                <FormLabel htmlFor='Language' color='blue.300'>Language</FormLabel>
                <SelectLanguage name='language' {...register('language')} />
            </FormControl>
            
            <FormControl>
                <FormLabel htmlFor='genres' color='blue.300'>Genres</FormLabel>
                <SelectGenre control={control} name='genre_id' type='movie' />
            </FormControl>

        </Stack>
    </form>
}