import { Flex } from '@mantine/core'
import { SliderWatched } from './slider-watched'

interface Props {}

export function HomeView({}: Props) {
    return (
        <Flex direction="column" gap="1rem" mx="-1rem">
            <SliderWatched />
            <SliderWatched />
            <SliderWatched />
            <SliderWatched />
            <SliderWatched />
            <SliderWatched />
            <SliderWatched />
            <SliderWatched />
            <SliderWatched />
        </Flex>
    )
}
