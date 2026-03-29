import { Select, SelectProps } from '@chakra-ui/react'
import { forwardRef } from 'react'


export const SelectSeriesUserSort = forwardRef<any, SelectProps>((props, ref) => {
    return <Select ref={ref} {...props}>
        <option value="popularity_desc">Popularity</option>
        <option value="rating_desc">IMDb Rating</option>
        <option value="user_rating_desc">Your rating</option>
        <option value="premiered_desc">Premiered DESC</option>
        <option value="premiered_asc">Premiered ASC</option>
        <option value="user_watchlist_added_at_desc">Added to watchlist at DESC</option>
        <option value="user_watchlist_added_at_asc">Added to watchlist at ASC</option>
        <option value="user_favorite_added_at_desc">Added to favorites at DESC</option>
        <option value="user_favorite_added_at_asc">Added to favorites at ASC</option>
        <option value="user_last_episode_watched_at_desc">Watched at DESC</option>
        <option value="user_last_episode_watched_at_asc">Watched at ASC</option>
    </Select>
})