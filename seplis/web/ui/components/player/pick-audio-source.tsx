import { Box, Flex } from '@chakra-ui/react'
import { IPlaySourceStream } from '@seplis/interfaces/play-server'
import { langCodeToLang } from '@seplis/utils'
import { stringToSourceStream } from './pick-subtitle-source'


interface IProps {
    audioSources: IPlaySourceStream[],
    selected?: IPlaySourceStream,
    onChange: (audioSource: IPlaySourceStream) => void
}

export function PickAudioSource({ audioSources, selected, onChange }: IProps) {
    return <Flex
        gap="0.25rem"
        direction="column">
        {audioSources.map(audio => (
            <Box
                key={audio.index}
                textStyle={selected?.index == audio.index ? 'selectedText' : null}
                cursor="pointer"
                onClick={() => onChange && onChange(audio)}
            >
                {audioSourceToName(audio)}
            </Box>
        ))}
    </Flex>
}


export function audioSourceToName(source: IPlaySourceStream) {
    if (!source) 
        return 'Unknown audio'
    else if (source.language && 
        (source.title === source.language) || (source.title === langCodeToLang(source.language) || !source.title))
        return `${langCodeToLang(source.language)}`
    else if (!source.language)
        return source.title
    else
        return `${langCodeToLang(source.language)} ${source.title}`
}


export function pickStartAudio(sourceStreams: IPlaySourceStream[], defaultAudio?: string) {
    const s = stringToSourceStream(defaultAudio, sourceStreams)
    if (s) return s
    for (const sub of sourceStreams) {
        if (sub.default || sub.forced)
            return sub
    }
    if (sourceStreams.length > 0)
        return sourceStreams[0]
}
