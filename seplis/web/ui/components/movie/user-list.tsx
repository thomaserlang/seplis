import { Box } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import ImageList from '@seplis/components/list'
import { IMovie } from '@seplis/interfaces/movie'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { BooleanParam, NumberParam, StringParam, useQueryParams, withDefault } from 'use-query-params'
import { MovieUserFilter } from './user-filter'


export default function MovieUserList({ title, url, emptyMessage }: { title: string, url: string, emptyMessage?: string | null }) {
    const { ref, focusKey, focusSelf } = useFocusable()
    const navigate = useNavigate()
    const location = useLocation()

    const [query, setQuery] = useQueryParams({
        sort: withDefault(StringParam, ""),
        genre_id: withDefault(NumberParam, 0),
        user_can_watch: withDefault(BooleanParam, localStorage.getItem('filter-user-can-watch') === 'true'),
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
                    urlParams={{
                        ...query,
                        'per_page': 50,
                    }}
                    parseItem={(movie) => (
                        {
                            key: `movie-${movie.id}`,
                            title: movie.title,
                            img: movie.poster_image?.url,
                        }
                    )}
                    onItemSelected={(movie: IMovie) => {
                        navigate(`/movies/${movie.id}`, {state: {
                            background: location
                        }})
                    }}
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
