import { FocusHandler, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { ISeriesUser } from '@seplis/interfaces/series'
import Slider from './slider'

interface IProps {
    onFocus?: FocusHandler,
}

export default function SliderRecentlyWatched(props: IProps) {    
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
        onFocus={props.onFocus}
    />
}