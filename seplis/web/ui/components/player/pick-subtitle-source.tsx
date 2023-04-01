import { Box, Flex } from '@chakra-ui/react'
import { IPlayServerRequestSource, IPlaySourceStream } from '@seplis/interfaces/play-server'
import { langCodeToLang } from '@seplis/utils'


interface IProps {
    subtitleSources: IPlaySourceStream[],
    selected?: IPlaySourceStream,
    onChange: (subtitleSource: IPlaySourceStream) => void
}


export function PickSubtitleSource({ subtitleSources, selected, onChange }: IProps) {
    return <Flex gap="0.25rem" direction="column">
        <Box
            textStyle={!selected ? 'selectedText' : null}
            cursor="pointer"
            onClick={() => onChange && onChange(null)}
        >
            Off
        </Box>
        {subtitleSources.map(subtitle => (
            <Box
                key={subtitle.index}
                textStyle={selected?.index == subtitle.index ? 'selectedText' : null}
                cursor="pointer"
                onClick={() => onChange && onChange(subtitle)}
            >
                {subtitleSourceToName(subtitle)}
            </Box>
        ))}
    </Flex>
}


export function subtitleSourceToName(source: IPlaySourceStream) {
    if (!source) return 'Off'
    
    if (!source.language && !source.title)
        return 'Unknown language'
    else if (source.title === source.language && source.language)
        return `${langCodeToLang(source.language)}`
    else if (!source.language)
        return source.title
    else
        return `${langCodeToLang(source.language)} (${source.title})`
}


export function pickStartSubtitle(requestSource: IPlayServerRequestSource, defaultSubtitle?: string) {
    if (defaultSubtitle == 'off')
        return
    const s = stringToSourceStream(defaultSubtitle, requestSource.source.subtitles)
    if (s) return s
    for (const sub of requestSource.source.subtitles) {
        if (sub.default || sub.forced)
            return sub
    }
}


export function stringToSourceStream(s: string, streams: IPlaySourceStream[]) {
    if (!s) return null
    const [lang, index] = s.toLowerCase().split(':')
    if (index !== undefined) {
        for (const stream of streams) {
            const l = stream?.language ?? stream?.title
            if (stream.index === parseInt(index) && (l) && (l.toLowerCase() === lang)) {
                return stream
            }
        }
    }
    for (const stream of streams) {
        const l = stream?.language ?? stream?.title
        if (l.toLowerCase() === lang) {
            return stream
        }
    }
    return null
}