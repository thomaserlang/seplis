import { Select, SelectProps } from '@chakra-ui/react'
import { forwardRef } from 'react'


export const SelectMovieUserSort = forwardRef<any, SelectProps>((props, ref) => {
    return <Select ref={ref} {...props} placeholder="Sort">
        <option value="stared_at_asc">Stared at ASC</option>
        <option value="stared_at_desc">Stared at DESC</option>
        <option value="watched_at_asc">Watched at ASC</option>
        <option value="watched_at_desc">Watched at DESC</option>
        <option value="rating_asc">Rating ASC</option>
        <option value="rating_desc">Rating DESC</option>
        <option value="popularity_asc">Popularity ASC</option>
        <option value="popularity_desc">Popularity DESC</option>
    </Select>
})