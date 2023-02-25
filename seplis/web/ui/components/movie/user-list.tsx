import { Box } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import ImageList from '@seplis/components/list'
import { IMovieUser } from '@seplis/interfaces/movie'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { NumberParam, StringParam, useQueryParams, withDefault } from 'use-query-params'
import { MovieUserFilter } from './user-filter'


export default function MovieUserList({ title, url }: { title: string, url: string }) {
    const { ref, focusKey, focusSelf } = useFocusable()
    const navigate = useNavigate()
    const location = useLocation()

    const [query, setQuery] = useQueryParams({
        sort: withDefault(StringParam, ""),
        genre_id: withDefault(NumberParam, 0),
    })

    useEffect(() => {
        focusSelf()
    }, [focusSelf])

    return <>
        <FocusContext.Provider value={focusKey}>
            <Box ref={ref}>
                <ImageList<IMovieUser>
                    title={title}
                    url={url}
                    urlParams={{
                        ...query,
                        'per_page': 50,
                    }}
                    parseItem={(item) => (
                        {
                            key: `movie-${item.movie.id}`,
                            title: item.movie.title,
                            img: item.movie.poster_image?.url,
                        }
                    )}
                    onItemSelected={(item: IMovieUser) => {
                        navigate(`/movies/${item.movie.id}`, {state: {
                            background: location
                        }})
                    }}
                    renderFilter={(options) => {
                        return <MovieUserFilter defaultValue={query} onSubmit={(data) => {
                            setQuery(data)
                            options.onClose()
                        }} />
                    }}
                />
            </Box>
        </FocusContext.Provider>
    </>
}
