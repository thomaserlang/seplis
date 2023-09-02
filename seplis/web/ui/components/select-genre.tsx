import { Box, FormControl, FormLabel, Switch } from '@chakra-ui/react'
import api from '@seplis/api'
import { IGenre } from '@seplis/interfaces/genre'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useController, Control } from 'react-hook-form'

export const SelectGenre = ({ control, name, type }: { control: Control<any, any>, name: string, type: 'series' | 'movie'}) => {
    const { isInitialLoading, data } = useQuery(['genres'], async () => {
        const result = await api.get<IGenre[]>('/2/genres', {
            params: {
                type: type,
            },
        })
        return result.data
    })
    const { field } = useController({ control, name })

    const [value, setValue] = useState<number[]>(field.value || [])

    if (isInitialLoading) return <Box>Loading Genres</Box>

    return <Box>
        {data && data.map(genre => (
            <FormControl key={`genre-${genre.id}`} display='flex' alignItems='center' justifyContent='space-between' mb='0.5rem'>
                <FormLabel htmlFor={`genre-${genre.id}`} flexGrow={1} mb='0' cursor='pointer'>
                    {genre.name}
                </FormLabel>
                <Switch 
                    id={`genre-${genre.id}`} 
                    size='lg' 
                    value={genre.id} 
                    isChecked={value.includes(genre.id)}
                    onChange={(e) => {
                        let v: number[]
                        if (e.target.checked) {
                            v = [...value, genre.id]
                        } else {
                            v = value.filter(v => v !== genre.id)
                        }
                        setValue(v)
                        field.onChange(v)
                    }}
                />
            </FormControl>
        ))}
    </Box>

}