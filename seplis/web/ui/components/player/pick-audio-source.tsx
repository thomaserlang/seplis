import { Box, Flex } from '@chakra-ui/react'
import { IPlayServerRequestSource, IPlaySourceStream } from '@seplis/interfaces/play-server'
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
    if (!source) return 'Off'
    return `${source.title} [${langCodeToLang(source.language)}]`
}


export function pickStartAudio(requestSource: IPlayServerRequestSource, defaultAudio?: string) {
    const s = stringToSourceStream(defaultAudio, requestSource.source.audio)
    if (s) return s
    for (const sub of requestSource.source.audio) {
        if (sub.default || sub.forced)
            return sub
    }
}
