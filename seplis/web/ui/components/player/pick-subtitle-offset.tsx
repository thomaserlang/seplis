import { Select } from '@chakra-ui/react'

export function PickSubtitleOffset({ selected = 0, onChange }: { selected: number, onChange: (offset: number) => void }) {
    return <Select value={selected} onChange={(event) => {
        onChange(parseFloat(event.currentTarget.value))
    }}>
        {[...Array(21)].map((v, i) => (
            <option key={`subOffset${i}`} value={(i/2-5)*-1}>{i/2-5} {(Math.abs(i/2-5) == 1)?'second':'seconds'}</option>
        ))}
    </Select>
}