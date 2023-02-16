import { Select, SelectProps } from '@chakra-ui/react'
import api from '@seplis/api'
import { IGenre } from '@seplis/interfaces/genre'
import { useQuery } from '@tanstack/react-query'
import { forwardRef } from 'react'

export const SelectGenre = forwardRef<any, SelectProps>((props, ref) => {
    const { isInitialLoading, data } = useQuery(['genres'], async () => {
        const result = await api.get<IGenre[]>('/2/genres')
        return result.data
    })

    return <Select ref={ref} {...props} placeholder={isInitialLoading ? 'Loading Genres' : 'All Genres'}>
        {data && data.map(genre => (
            <option key={genre.id} value={genre.id}>{genre.name}</option>
        ))}
    </Select>
})