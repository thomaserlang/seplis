import { Slider, SliderFilledTrack, SliderThumb, SliderTrack } from '@chakra-ui/react'

export default function VolumeBar({ defaultVolume, onChange }: { defaultVolume: number, onChange: (volume: number) => void }) {
    return <Slider
        aria-label="Volume"
        defaultValue={defaultVolume*10}
        min={0}
        max={10}
        orientation="vertical"
        minH='32'
        onChange={(value) => onChange(value/10)}
    >
        <SliderTrack width="15px">
            <SliderFilledTrack/>
        </SliderTrack>
        <SliderThumb boxSize={6} />
    </Slider>
}