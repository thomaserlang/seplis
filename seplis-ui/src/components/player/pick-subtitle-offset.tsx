import { Box, Button, Flex, Select, Slider, SliderMark, SliderThumb, SliderTrack, Text } from '@chakra-ui/react'
import { useEffect, useState } from 'react'

export function PickSubtitleOffset({ selected = 0, onChange }: { selected: number, onChange: (offset: number) => void }) {
    const [value, setValue] = useState(selected * -1)

    useEffect(() => {
        if (value !== selected)
            setValue(selected * -1)
    }, [selected])

    const labelStyles = {
        mt: '20px',
        ml: '-1',
    }

    const labelStylesMinus = {
        mt: '20px',
        ml: '-2',
    }

    return <Flex mb="2rem" mt="3rem" alignItems="center" direction="column">
        <Slider size="lg" value={value} min={-10} max={10} step={0.5} onChange={setValue} onChangeEnd={(v) => onChange(v * -1)}>
            <SliderMark value={-10} {...labelStylesMinus}>
                -10
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
            <SliderMark value={10} {...labelStyles}>
                10
            </SliderMark>
            <SliderMark
                value={0}
                color='white'
                mt='-50px'
                ml='-40px'
            >
                {value} seconds
            </SliderMark>
            <SliderTrack boxSize={6} />
            <SliderThumb boxSize={10} />
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