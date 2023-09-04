import { Select, SelectProps } from '@chakra-ui/react'
import { forwardRef } from 'react'


export const SelectMovieUserSort = forwardRef<any, SelectProps>((props, ref) => {
    return <Select ref={ref} {...props}>
        <option value="popularity_desc">Popularity</option>
        <option value="rating_desc">IMDb Rating</option>
        <option value="release_date_desc">Release Date DESC</option>
        <option value="release_date_asc">Release Date ASC</option>
        <option value="user_watchlist_added_at_desc">Added to watchlist at DESC</option>
        <option value="user_watchlist_added_at_asc">Added to watchlist at ASC</option>
        <option value="user_favorite_added_at_desc">Added to favorites at DESC</option>
        <option value="user_favorite_added_at_asc">Added to favorites at ASC</option>
        <option value="user_last_watched_at_desc">Watched at DESC</option>
        <option value="user_last_watched_at_asc">Watched at ASC</option>
    </Select>
})