import { Flex, Box } from '@chakra-ui/react'
import { IPlayServerRequestSource, IPlayServerRequestSources, IPlaySourceStream } from '@seplis/interfaces/play-server'
import { PickAudioSource } from './pick-audio-source'
import { PickQuality } from './pick-quality'
import { PickSource } from './pick-source'
import { PickSubtitleSource } from './pick-subtitle-source'

export interface ISettingsProps {
    playServers: IPlayServerRequestSources[],
    requestSource: IPlayServerRequestSource,
    resolutionWidth?: number,
    audioSource?: IPlaySourceStream,
    subtitleSource?: IPlaySourceStream,
    onRequestSourceChange?: (requestSource: IPlayServerRequestSource) => void,
    onResolutionWidthChange?: (width: number) => void,
    onAudioSourceChange?: (audioSource: IPlaySourceStream) => void,
    onSubtitleSourceChange?: (subtitleSource: IPlaySourceStream) => void,
}

export function Settings({ 
    playServers, 
    requestSource, 
    resolutionWidth,
    audioSource,
    subtitleSource,
    onRequestSourceChange,
    onResolutionWidthChange,
    onAudioSourceChange,
    onSubtitleSourceChange,
}: ISettingsProps) {
    return <Flex wrap="wrap" gap="1rem">
        <Flex basis="150px" direction="column">
            <Box textStyle="h2">Sources</Box>
            <PickSource 
                playServers={playServers} 
                selected={requestSource} 
                onChange={onRequestSourceChange}    
            />
        </Flex>

        <Flex basis="150px" direction="column">
            <Box textStyle="h2">Quality</Box>
            <PickQuality 
                source={requestSource.source} 
                selectedWidth={resolutionWidth} 
                onChange={onResolutionWidthChange} 
            />
        </Flex>

        <Flex basis="250px" grow="1" direction="column">
            <Box textStyle="h2">Audio</Box>
            <PickAudioSource 
                audioSources={requestSource.source.audio}
                selected={audioSource}
                onChange={onAudioSourceChange}
            />
        </Flex>


        <Flex basis="250px" grow="1" direction="column">
            <Box textStyle="h2">Subtitles</Box>
            <PickSubtitleSource
                subtitleSources={requestSource.source.subtitles}
                selected={subtitleSource}
                onChange={onSubtitleSourceChange}
            />
        </Flex>


        <Flex basis="150px" grow="1" direction="column">
            <Box textStyle="h2">Subtitle offset</Box>
            <Box></Box>
        </Flex>

    </Flex>
}