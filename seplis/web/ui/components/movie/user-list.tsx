import { Box } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import ImageList from '@seplis/components/list'
import { IMovie } from '@seplis/interfaces/movie'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { BooleanParam, NumberParam, NumericArrayParam, StringParam, searchStringToObject, useQueryParams, withDefault } from 'use-query-params'
import { IUserFilterData, MovieUserFilter } from './user-filter'
import { ISliderItem } from '@seplis/interfaces/slider'


interface IProps<S = IMovie>{
    title: string
    url: string
    defaultSort?: string | null
    emptyMessage?: string | null,
    onItemSelected?: (item: S) => void
    parseItem?: (item: S) => ISliderItem
}


export default function MovieUserList<S = IMovie>({ 
    title, 
    url, 
    emptyMessage, 
    defaultSort,
    onItemSelected,
    parseItem,
}: IProps<S>) {
    const { ref, focusKey, focusSelf } = useFocusable()
    const navigate = useNavigate()
    const location = useLocation()

    const [query, setQuery] = useQueryParams({
        sort: withDefault(StringParam, defaultSort),
        genre_id: withDefault(NumericArrayParam, []),
        user_can_watch: withDefault(BooleanParam, localStorage.getItem('filter-user-can-watch') === 'true'),
        release_date_gt: StringParam,
        release_date_lt: StringParam,
        rating_gt: NumberParam,
        rating_lt: NumberParam,
        rating_votes_gt: NumberParam,
        language: StringParam,
        user_has_watched: StringParam,
    }, {
        searchStringToObject: () => {
            // Prevent using the the actual location.search string when the movie modal is open
            // so the background update when the actual location.search changes
            return searchStringToObject(location.search)
        }
    })

    useEffect(() => {
        focusSelf()
    }, [focusSelf])

    return <>
        <FocusContext.Provider value={focusKey}>
            <Box ref={ref}>
                <ImageList<IMovie>
                    title={title}
                    url={url}
                    emptyMessage={emptyMessage}
                    filtersActive={isFilterActive(query)}
                    urlParams={{
                        ...query,
                        'per_page': 50,
                    }}
                    parseItem={parseItem || ((movie) => (
                        {
                            key: `movie-${movie.id}`,
                            title: movie.title,
                            img: movie.poster_image?.url,
                        }
                    ))}
                    onItemSelected={onItemSelected || ((movie: IMovie) => {
                        navigate(`/movies/${movie.id}`, {state: {
                            background: location
                        }})
                    })}
                    renderFilter={(options) => {
                        return <MovieUserFilter defaultValue={query} onSubmit={(data) => {
                            setQuery(data)
                            if (data.user_can_watch === true) 
                                localStorage.setItem('filter-user-can-watch', 'true')
                            else
                                localStorage.removeItem('filter-user-can-watch')
                        }} />
                    }}
                />
            </Box>
        </FocusContext.Provider>
    </>
}


function isFilterActive(query: IUserFilterData) {
    return query.genre_id?.length > 0
           || query.user_can_watch === true 
           || query.release_date_gt != null
           || query.release_date_lt != null
           || query.rating_gt != null
           || query.rating_lt != null
           || query.rating_votes_gt != null
           || query.language != null
           || query.user_has_watched != null
}