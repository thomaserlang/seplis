import { Select, SelectProps } from '@chakra-ui/react'
import { forwardRef } from 'react'


export const SelectSeriesUserSort = forwardRef<any, SelectProps>((props, ref) => {
    return <Select ref={ref} {...props} placeholder="Sort">
        <option value="followed_at_asc">Followed at ASC</option>
        <option value="followed_at_desc">Followed at DESC</option>
        <option value="user_rating_asc">Your rating ASC</option>
        <option value="user_rating_desc">Your rating DESC</option>
        <option value="watched_at_asc">Watched at ASC</option>
        <option value="watched_at_desc">Watched at DESC</option>
        <option value="rating_asc">Rating ASC</option>
        <option value="rating_desc">Rating DESC</option>
    </Select>
})