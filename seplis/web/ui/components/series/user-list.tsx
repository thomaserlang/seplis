import { Box } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import ImageList from '@seplis/components/list'
import { ISeries } from '@seplis/interfaces/series'
import { ISliderItem } from '@seplis/interfaces/slider'
import { ReactNode, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { NumberParam, StringParam, useQueryParams, withDefault } from 'use-query-params'
import { SeriesUserFilter } from '../../components/series/user-filter'

interface IProps<S = ISeries>{
    title: string
    url: string
    defaultSort?: string
    emptyMessage?: string | null,
    onItemSelected?: (item: S) => void
    parseItem?: (item: S) => ISliderItem
}

export default function UserSeriesList<S = ISeries>({ 
    title, 
    url, 
    defaultSort, 
    emptyMessage,
    parseItem, 
    onItemSelected
}: IProps<S>) {
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
                <ImageList<S>
                    title={title}
                    url={url}
                    emptyMessage={emptyMessage}
                    urlParams={{
                        ...query,
                        'per_page': 50,
                    }}
                    parseItem={parseItem || ((series) => (
                        {
                            key: `series-${series.id}`,
                            title: series.title,
                            img: series.poster_image?.url,
                        }
                    ))}
                    onItemSelected={onItemSelected || ((series: ISeries) => {
                        navigate(`/series/${series.id}`, {state: {
                            background: location
                        }})
                    })}
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
