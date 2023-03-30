import { Flex, Box, Menu, MenuButton, forwardRef, Portal, MenuList, MenuItem, useDisclosure, Modal, ModalOverlay, ModalContent, ModalCloseButton, ModalBody, IconButton, Popover, PopoverTrigger, PopoverContent, PopoverHeader, PopoverCloseButton, PopoverBody, PopoverAnchor } from '@chakra-ui/react'
import { IPlayServerRequestSource, IPlayServerRequestSources, IPlaySourceStream } from '@seplis/interfaces/play-server'
import { ReactNode, useState } from 'react'
import { FaCog } from 'react-icons/fa'
import { audioSourceToName, PickAudioSource } from './pick-audio-source'
import { PickQuality, resolutionToText } from './pick-quality'
import { PickSource, renderPlaySource } from './pick-source'
import { PickSubtitleOffset, SubtitleOffsetToText } from './pick-subtitle-offset'
import { PickSubtitleSource, subtitleSourceToName } from './pick-subtitle-source'

export interface ISettingsProps {
    playServers: IPlayServerRequestSources[],
    requestSource: IPlayServerRequestSource,
    resolutionWidth?: number,
    audioSource?: IPlaySourceStream,
    subtitleSource?: IPlaySourceStream,
    subtitleOffset?: number,
    onRequestSourceChange?: (requestSource: IPlayServerRequestSource) => void,
    onResolutionWidthChange?: (width: number) => void,
    onAudioSourceChange?: (audioSource: IPlaySourceStream) => void,
    onSubtitleSourceChange?: (subtitleSource: IPlaySourceStream) => void,
    onSubtitleOffsetChange?: (offset: number) => void,
}

export function SettingsMenu({
    playServers,
    requestSource,
    resolutionWidth,
    audioSource,
    subtitleSource,
    subtitleOffset,
    onRequestSourceChange,
    onResolutionWidthChange,
    onAudioSourceChange,
    onSubtitleSourceChange,
    onSubtitleOffsetChange,
}: ISettingsProps) {
    const [nested, setNested] = useState<string>(null)
    return <>
        <Popover isOpen={nested !== null} onClose={() => setNested(null)}>
            <Menu autoSelect={false}>
                <PopoverAnchor>
                    <MenuButton
                        as={IconButton}
                        aria-label="Settings"
                        icon={<FaCog />}
                        size="lg"
                        fontSize="28px"
                    />
                </PopoverAnchor>
                <MenuList>
                    <MenuItem command={renderPlaySource(requestSource.source)} onClick={() => setNested('sources')}>
                        Source
                    </MenuItem>
                    <MenuItem command={resolutionToText(resolutionWidth)} onClick={() => setNested('quality')}>
                        Quality
                    </MenuItem>
                    <MenuItem command={audioSourceToName(audioSource)} onClick={() => setNested('audio')}>
                        Audio
                    </MenuItem>
                    <MenuItem command={subtitleSourceToName(subtitleSource)} onClick={() => setNested('subtitles')}>
                        Subtitles ({requestSource.source?.subtitles?.length})
                    </MenuItem>
                    <MenuItem command={SubtitleOffsetToText(subtitleOffset)} onClick={() => setNested('subtitle_offset')}>
                        Subtitle offset
                    </MenuItem>
                </MenuList>
            </Menu>

            <PopoverContent>
                <PopoverCloseButton />

                {nested == 'sources' && <>
                    <PopoverHeader>Sources</PopoverHeader>
                    <PopoverBody>
                        <PickSource
                            playServers={playServers}
                            selected={requestSource}
                            onChange={onRequestSourceChange}
                        />
                    </PopoverBody>
                </>}

                {nested == 'quality' && <>
                    <PopoverHeader>Quality</PopoverHeader>
                    <PopoverBody>
                        <PickQuality
                            source={requestSource.source}
                            selectedWidth={resolutionWidth}
                            onChange={onResolutionWidthChange}
                        />
                    </PopoverBody>
                </>}

                {nested == 'audio' && <>
                    <PopoverHeader>Audio</PopoverHeader>
                    <PopoverBody>
                        <Box maxHeight="35vh" overflow="auto">
                            <PickAudioSource
                                audioSources={requestSource.source.audio}
                                selected={audioSource}
                                onChange={onAudioSourceChange}
                            />
                        </Box>
                    </PopoverBody>
                </>}

                {nested == 'subtitles' && <>
                    <PopoverHeader>Subtitles</PopoverHeader>
                    <PopoverBody>
                        <Box maxHeight="35vh" overflow="auto">
                            <PickSubtitleSource
                                subtitleSources={requestSource.source.subtitles}
                                selected={subtitleSource}
                                onChange={onSubtitleSourceChange}
                            />
                        </Box>
                    </PopoverBody>
                </>}

                {nested == 'subtitle_offset' && <>
                    <PopoverHeader>Subtitle offset</PopoverHeader>
                    <PopoverBody>
                        <PickSubtitleOffset selected={subtitleOffset} onChange={onSubtitleOffsetChange} />
                    </PopoverBody>
                </>}

            </PopoverContent>
        </Popover>
    </>
}