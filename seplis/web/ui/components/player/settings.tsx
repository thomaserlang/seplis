import { Flex, Box } from '@chakra-ui/react'
import { IPlayServerRequestSource, IPlayServerRequestSources } from '@seplis/interfaces/play-server'
import { PickQuality } from './pick-quality'
import { PickSource } from './pick-source'

export interface ISettingsProps {
    playServers: IPlayServerRequestSources[],
    selectedRequestSource: IPlayServerRequestSource,
    onRequestSourceChange?: (requestSource: IPlayServerRequestSource) => void,
}

export function Settings({ playServers, selectedRequestSource, onRequestSourceChange }: ISettingsProps) {
    return <Flex wrap="wrap" gap="1rem">
        <Flex basis="150px" direction="column">
            <Box textStyle="h2">Sources</Box>
            <PickSource 
                playServers={playServers} 
                selected={selectedRequestSource} 
                onChange={onRequestSourceChange}    
            />
        </Flex>

        <Flex basis="150px" direction="column">
            <Box textStyle="h2">Quality</Box>
            <PickQuality source={selectedRequestSource.source} />
        </Flex>

        <Flex basis="150px" grow="1" direction="column">
            <Box textStyle="h2">Audio</Box>
            <Box></Box>
        </Flex>


        <Flex basis="150px" grow="1" direction="column">
            <Box textStyle="h2">Subtitles</Box>
            <Box></Box>
        </Flex>


        <Flex basis="150px" grow="1" direction="column">
            <Box textStyle="h2">Subtitle offset</Box>
            <Box></Box>
        </Flex>

    </Flex>
}