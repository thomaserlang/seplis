import { Select, SelectProps } from '@chakra-ui/react'
import { forwardRef } from 'react'


export const SelectSeriesUserSort = forwardRef<any, SelectProps>((props, ref) => {
    return <Select ref={ref} {...props} placeholder="Sort">
        <option value="user_followed_at_asc">Followed at ASC</option>
        <option value="user_followed_at_desc">Followed at DESC</option>
        <option value="user_rating_asc">Your rating ASC</option>
        <option value="user_rating_desc">Your rating DESC</option>
        <option value="user_last_episode_watched_at_asc">Watched at ASC</option>
        <option value="user_last_episode_watched_at_desc">Watched at DESC</option>
        <option value="rating_asc">Rating ASC</option>
        <option value="rating_desc">Rating DESC</option>
        <option value="popularity_asc">Popularity ASC</option>
        <option value="popularity_desc">Popularity DESC</option>
    </Select>
})