import { Select } from '@chakra-ui/react'

export function PickSubtitleOffset({ selected = 0, onChange }: { selected: number, onChange: (offset: number) => void }) {
    return <Select value={selected} onChange={(event) => {
        onChange(parseFloat(event.currentTarget.value))
    }}>
        {[...Array(73)].map((v, i) => {
            const a = i/2-18
            return <option key={`subOffset${i}`} value={a*-1}>{a} {(Math.abs(a) == 1)?'second':'seconds'}</option>
        })}
    </Select>
}