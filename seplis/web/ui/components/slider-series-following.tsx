import api from '@seplis/api'
import { IPageResult } from '@seplis/interfaces/page'
import { ISeriesUser } from '@seplis/interfaces/series'
import { ISliderItem } from '@seplis/interfaces/slider'
import { useQuery } from '@tanstack/react-query'
import Slider from './slider'

export default function SliderSeriesFollowing() {
    return <Slider<ISeriesUser>
        title="Following" 
        url="/2/users/me/series-following"
        parseItem={(item) => (
            {
                key: `series-${item.series.id}`,
                title: item.series.title,
                img: item.series.poster_image?.url,
            }
        )}
    />
}