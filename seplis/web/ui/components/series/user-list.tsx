import { Box } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import ImageList from '@seplis/components/list'
import { ISeries } from '@seplis/interfaces/series'
import { ISliderItem } from '@seplis/interfaces/slider'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { BooleanParam, NumberParam, NumericArrayParam, StringParam, useQueryParams, withDefault } from 'use-query-params'
import { IUserFilterData, SeriesUserFilter } from '../../components/series/user-filter'
import { searchStringToObject } from 'serialize-query-params'

interface IProps<S = ISeries>{
    title: string
    url: string
    defaultSort?: string | null
    emptyMessage?: string | null,
    showFilterButton?: boolean,
    onItemSelected?: (item: S) => void
    parseItem?: (item: S) => ISliderItem
}

export default function UserSeriesList<S = ISeries>({ 
    title, 
    url, 
    defaultSort, 
    emptyMessage,
    showFilterButton=true,
    parseItem, 
    onItemSelected
}: IProps<S>) {
    const { ref, focusKey, focusSelf } = useFocusable()
    const navigate = useNavigate()
    const location = useLocation()

    const [query, setQuery] = useQueryParams({
        sort: withDefault(StringParam, defaultSort),
        genre_id: withDefault(NumericArrayParam, []),
        user_can_watch: withDefault(BooleanParam, localStorage.getItem('filter-user-can-watch') === 'true'),
        premiered_gt: StringParam,
        premiered_lt: StringParam,
        rating_gt: NumberParam,
        rating_lt: withDefault(NumberParam, 10),
        rating_votes_gt: NumberParam,
        language: StringParam,
        user_has_watched: StringParam,
    }, {
        searchStringToObject: () => {
            // Prevent using the the actual location.search string when the series modal is open
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
                <ImageList<S>
                    title={title}
                    url={url}
                    emptyMessage={emptyMessage}
                    filtersActive={isFilterActive(query)}
                    showFilterButton={showFilterButton}
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
           || query.premiered_gt != null
           || query.premiered_lt != null
           || (query.rating_gt != null && query.rating_gt !== 0)
           || (query.rating_lt != null && query.rating_lt !== 10)
           || query.rating_votes_gt != null
           || query.language != null
           || query.user_has_watched != null
}