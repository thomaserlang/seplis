import { Box, Button, Flex, Select, Slider, SliderMark, SliderThumb, SliderTrack, Text } from '@chakra-ui/react'
import { useEffect, useState } from 'react'

export function PickSubtitleOffset({ selected = 0, onChange }: { selected: number, onChange: (offset: number) => void }) {
    const [value, setValue] = useState(selected * -1)

    useEffect(() => {
        if (value !== selected)
            setValue(selected * -1)
    }, [selected])

    const labelStyles = {
        mt: '2',
        ml: '-1',
        fontSize: 'sm',
    }

    const labelStylesMinus = {
        mt: '2',
        ml: '-2',
        fontSize: 'sm',
    }

    return <Flex mb="2rem" mt="3rem" alignItems="center" direction="column">
        <Slider value={value} min={-30} max={30} step={0.5} onChange={setValue} onChangeEnd={(v) => onChange(v * -1)}>
            <SliderMark value={-30} {...labelStylesMinus}>
                -30
            </SliderMark>
            <SliderMark value={-4} {...labelStylesMinus}>
                -4
            </SliderMark>
            <SliderMark value={-2} {...labelStylesMinus}>
                -2
            </SliderMark>
            <SliderMark value={0} {...labelStyles}>
                0
            </SliderMark>
            <SliderMark value={2} {...labelStyles}>
                2
            </SliderMark>
            <SliderMark value={4} {...labelStyles}>
                4
            </SliderMark>
            <SliderMark value={30} {...labelStyles}>
                30
            </SliderMark>
            <SliderMark
                value={0}
                color='white'
                mt='-10'
                ml='-5'
            >
                {value} secs
            </SliderMark>
            <SliderTrack>
            </SliderTrack>
            <SliderThumb />
        </Slider>

        <Box mt="4rem">
            <Button size="lg" onClick={() => onChange(null)}>Close</Button>
        </Box>
    </Flex>
}

export function SubtitleOffsetToText(offset: number) {
    const v = (offset * -1) || 0
    return `${v} ${Math.abs(v) == 1 ? 'sec' : 'secs'}`
}