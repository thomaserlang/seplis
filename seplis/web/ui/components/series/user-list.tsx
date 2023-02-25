import { Box } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import ImageList from '@seplis/components/list'
import { ISeriesUser } from '@seplis/interfaces/series'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { NumberParam, StringParam, useQueryParams, withDefault } from 'use-query-params'
import { SeriesUserFilter } from '../../components/series/user-filter'


export default function SeriesUserList({ title, url }: { title: string, url: string }) {
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
                <ImageList<ISeriesUser>
                    title={title}
                    url={url}
                    urlParams={{
                        ...query,
                        'per_page': 50,
                    }}
                    parseItem={(item) => (
                        {
                            key: `series-${item.series.id}`,
                            title: item.series.title,
                            img: item.series.poster_image?.url,
                        }
                    )}
                    onItemSelected={(item: ISeriesUser) => {
                        navigate(`/series/${item.series.id}`, {state: {
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
