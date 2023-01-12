import { ISeriesUser } from '@seplis/interfaces/series'
import Slider from './slider'

export default function SliderRecentlyWatched() {      
    
    return <Slider<ISeriesUser>
        title="Watched" 
        url="/2/users/me/series-watched"
        parseItem={(item) => (
            {
                key: `series-${item.series.id}`,
                title: item.series.title,
                img: item.series.poster_image?.url,
            }
        )}
    />
}