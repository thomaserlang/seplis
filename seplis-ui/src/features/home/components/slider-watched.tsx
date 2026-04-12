import { PosterImage } from '@/components/poster-image/poster-image'
import { Slider } from '@/components/slider'
import { mediaTypes } from '@/features/media-type'
import { useGetUserWatched } from '@/features/user'
import { UserWatched } from '@/features/user/types/user-watched.types'
import { pageItemsFlatten } from '@/utils/api-crud'

interface Props {
    onClick?: (item: UserWatched) => void
    title?: string
}

export function SliderWatched({ onClick, title }: Props) {
    const { data, isLoading, fetchNextPage } = useGetUserWatched({
        params: {
            user_can_watch: true,
        },
    })
    const items = pageItemsFlatten(data)

    return (
        <Slider
            title={title}
            items={items}
            isLoading={isLoading}
            onLoadMore={fetchNextPage}
            onClick={onClick}
            emptyMessage="You haven't watched anything that's available on a play server."
            renderItem={(item) => (
                <PosterImage
                    posterImage={item.data.poster_image}
                    title={item.data.title}
                />
            )}
            renderHoverCard={(item) =>
                mediaTypes[item.type].renderHoverCard({
                    data: item[item.type],
                })
            }
        />
    )
}
