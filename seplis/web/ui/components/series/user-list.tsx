import { Box } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import ImageList from '@seplis/components/list'
import { ISeries } from '@seplis/interfaces/series'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { NumberParam, StringParam, useQueryParams, withDefault } from 'use-query-params'
import { SeriesUserFilter } from '../../components/series/user-filter'


export default function UserSeriesList({ title, url, defaultSort }: { title: string, url: string, defaultSort: string }) {
    const { ref, focusKey, focusSelf } = useFocusable()
    const navigate = useNavigate()
    const location = useLocation()

    const [query, setQuery] = useQueryParams({
        sort: withDefault(StringParam, defaultSort),
        genre_id: withDefault(NumberParam, 0),
    })

    useEffect(() => {
        focusSelf()
    }, [focusSelf])

    return <>
        <FocusContext.Provider value={focusKey}>
            <Box ref={ref}>
                <ImageList<ISeries>
                    title={title}
                    url={url}
                    urlParams={{
                        ...query,
                        'per_page': 50,
                    }}
                    parseItem={(series) => (
                        {
                            key: `series-${series.id}`,
                            title: series.title,
                            img: series.poster_image?.url,
                        }
                    )}
                    onItemSelected={(series: ISeries) => {
                        navigate(`/series/${series.id}`, {state: {
                            background: location
                        }})
                    }}
                    renderFilter={(options) => {
                        return <SeriesUserFilter defaultValue={query} onSubmit={(data) => {
                            setQuery(data)
                            options.onClose()
                        }} />
                    }}
                />
            </Box>
        </FocusContext.Provider>
    </>
}
