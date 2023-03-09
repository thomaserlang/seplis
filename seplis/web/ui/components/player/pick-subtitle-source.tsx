import { Box } from '@chakra-ui/react'
import { IPlayServerRequestSource, IPlaySourceStream } from '@seplis/interfaces/play-server'
import { langCodeToLang } from '@seplis/utils'


interface IProps {
    subtitleSources: IPlaySourceStream[],
    selected?: IPlaySourceStream,
    onChange: (subtitleSource: IPlaySourceStream) => void
}

export function PickSubtitleSource({ subtitleSources, selected, onChange }: IProps) {
    return <Box>
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
                {subtitle.title} [{langCodeToLang(subtitle.language)}]
            </Box>
        ))}
    </Box>
}


export function pickStartSubtitle(requestSource: IPlayServerRequestSource, defaultSubtitle: string) {
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