import { Box } from '@chakra-ui/react'
import { IPlaySourceStream } from '@seplis/interfaces/play-server'
import { langCodeToLang } from '@seplis/utils'


interface IProps {
    audioSources: IPlaySourceStream[],
    selected?: IPlaySourceStream,
    onChange: (audioSource: IPlaySourceStream) => void
}

export function PickAudioSource({ audioSources, selected, onChange }: IProps) {
    return <Box>
        {audioSources.map(audio => (
            <Box 
                key={audio.index}
                textStyle={selected?.index == audio.index ? 'selectedText' : null}
                cursor="pointer"
                onClick={() => onChange && onChange(audio)}
            >
                {audio.title} [{langCodeToLang(audio.language)}]
            </Box>
        ))}
    </Box>
}
