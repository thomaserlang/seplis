import api from '@seplis/api'
import { IPageResult } from '@seplis/interfaces/page'
import { ISeriesUser } from '@seplis/interfaces/series'
import { ISliderItem } from '@seplis/interfaces/slider'
import { useQuery } from '@tanstack/react-query'
import Slider from './slider'

export default function SliderSeriesFollowing() {
    const { data, isInitialLoading, error, isFetching } = 
        useQuery(['seriesFollowing', {}], async () => {
            const data = await api.get<IPageResult<ISeriesUser>>('/2/users/me/series-following', {
                params: {
                    per_page: 12,
                }
            })
            const items: ISliderItem[] = []
            for (const item of data.data.items) {
                items.push({
                    key: `series-${item.series.id}`,
                    title: item.series.title,
                    img: item.series.poster_image?.url,
                })
            }
            return items
        }, { keepPreviousData: true })

    return <Slider title="Following" items={data} isLoading={isInitialLoading} />
}