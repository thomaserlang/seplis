import { Slider } from '@/components/slider'
import { mediaTypes } from '@/features/media-type'
import { useGetUserWatched } from '@/features/user'
import { pageItemsFlatten } from '@/utils/api-crud'
import { Image } from '@mantine/core'
import { useSearchParams } from 'react-router-dom'

interface Props {}

export function SliderWatched({}: Props) {
    const [_, setParams] = useSearchParams()
    const { data, isLoading, fetchNextPage } = useGetUserWatched({
        params: {
            user_can_watch: true,
        },
    })
    const items = pageItemsFlatten(data)

    const handleClick = (item: (typeof items)[number]) => {
        setParams((params) => {
            params.set('mid', `${item.type}-${item.data.id}`)
            return params
        })
    }

    return (
        <Slider
            items={items}
            isLoading={isLoading}
            onLoadMore={fetchNextPage}
            renderItem={(item) => (
                <Image
                    src={`${item.data.poster_image?.url}@SX320.webp`}
                    radius="sm"
                    onClick={() => handleClick(item)}
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
