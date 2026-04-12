import { Slider } from '@/components/slider'
import { useGetUserWatched } from '@/features/user'
import { pageItemsFlatten } from '@/utils/api-crud'
import { Image } from '@mantine/core'

interface Props {}

export function SliderWatched({}: Props) {
    const { data, isLoading, fetchNextPage } = useGetUserWatched({
        params: {
            user_can_watch: true,
        },
    })
    const items = pageItemsFlatten(data)
    return (
        <Slider
            items={items}
            isLoading={isLoading}
            onLoadMore={fetchNextPage}
            renderItem={(item) => (
                <Image
                    src={`${item.data.poster_image?.url}@SX320.webp`}
                    radius="sm"
                />
            )}
            renderHoverCard={(item) => (
                <div className="hoverCard">
                    <Image
                        src={`${item.data.poster_image?.url}@SX320.webp`}
                        radius="sm"
                    />
                </div>
            )}
        />
    )
}
