import {
    Box,
    IconButton,
    Menu,
    MenuButton,
    MenuItem,
    MenuList,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalHeader,
    Popover,
    PopoverAnchor,
    PopoverBody,
    PopoverCloseButton,
    PopoverContent,
    PopoverHeader,
} from '@chakra-ui/react'
import {
    IPlayServerRequestSource,
    IPlayServerRequestSources,
    IPlaySourceStream,
} from '@seplis/interfaces/play-server'
import { useState } from 'react'
import { FaCog } from 'react-icons/fa'
import { audioSourceToName, PickAudioSource } from './pick-audio-source'
import { PickQuality, resolutionToText } from './pick-quality'
import { PickSource, renderPlaySource } from './pick-source'
import {
    PickSubtitleOffset,
    SubtitleOffsetToText,
} from './pick-subtitle-offset'
import {
    PickSubtitleSource,
    subtitleSourceToName,
} from './pick-subtitle-source'

export interface ISettingsProps {
    playServers: IPlayServerRequestSources[]
    requestSource: IPlayServerRequestSource
    resolutionWidth?: number
    audioSource?: IPlaySourceStream
    subtitleSource?: IPlaySourceStream
    subtitleOffset?: number
    forceTranscode?: boolean
    onRequestSourceChange?: (requestSource: IPlayServerRequestSource) => void
    onResolutionWidthChange?: (width: number) => void
    onAudioSourceChange?: (audioSource: IPlaySourceStream) => void
    onSubtitleSourceChange?: (subtitleSource: IPlaySourceStream) => void
    onSubtitleOffsetChange?: (offset: number) => void
    onForceTranscodeChange?: (forceTranscode: boolean) => void
    containerRef?: React.RefObject<HTMLElement | null>
}

export function SettingsMenu({
    playServers,
    requestSource,
    resolutionWidth,
    audioSource,
    subtitleSource,
    subtitleOffset,
    forceTranscode,
    onRequestSourceChange,
    onResolutionWidthChange,
    onAudioSourceChange,
    onSubtitleSourceChange,
    onSubtitleOffsetChange,
    onForceTranscodeChange,
    containerRef,
}: ISettingsProps) {
    const [nested, setNested] = useState<string>(null)
    const [showModal, setShowModal] = useState<string>(null)
    return (
        <>
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
                        <MenuItem
                            isDisabled={
                                !(
                                    playServers.length > 1 ||
                                    playServers[0]?.sources?.length > 1
                                )
                            }
                            command={renderPlaySource(requestSource.source)}
                            onClick={() => setNested('sources')}
                        >
                            Source
                        </MenuItem>
                        <MenuItem
                            command={resolutionToText(resolutionWidth)}
                            onClick={() => setNested('quality')}
                        >
                            Quality
                        </MenuItem>
                        <MenuItem
                            command={audioSourceToName(audioSource)}
                            onClick={() => setNested('audio')}
                            isDisabled={
                                !(requestSource.source?.audio?.length > 1)
                            }
                        >
                            Audio
                        </MenuItem>
                        <MenuItem
                            isDisabled={
                                !requestSource.source?.subtitles?.length
                            }
                            command={subtitleSourceToName(subtitleSource)}
                            onClick={() => setNested('subtitles')}
                        >
                            Subtitle
                        </MenuItem>
                        <MenuItem
                            command={SubtitleOffsetToText(subtitleOffset)}
                            onClick={() => setShowModal('subtitle_offset')}
                        >
                            Subtitle offset
                        </MenuItem>
                        <MenuItem
                            command={forceTranscode ? 'On' : 'Off'}
                            onClick={() =>
                                onForceTranscodeChange?.(!forceTranscode)
                            }
                        >
                            Force transcode
                        </MenuItem>
                    </MenuList>
                </Menu>

                <PopoverContent>
                    <PopoverCloseButton />

                    {nested == 'sources' && (
                        <>
                            <PopoverHeader>Sources</PopoverHeader>
                            <PopoverBody>
                                <PickSource
                                    playServers={playServers}
                                    selected={requestSource}
                                    onChange={(s) => {
                                        onRequestSourceChange(s)
                                        setNested(null)
                                    }}
                                />
                            </PopoverBody>
                        </>
                    )}

                    {nested == 'quality' && (
                        <>
                            <PopoverHeader>Quality</PopoverHeader>
                            <PopoverBody>
                                <PickQuality
                                    source={requestSource.source}
                                    selectedWidth={resolutionWidth}
                                    onChange={(width) => {
                                        onResolutionWidthChange(width)
                                        setNested(null)
                                    }}
                                />
                            </PopoverBody>
                        </>
                    )}

                    {nested == 'audio' && (
                        <>
                            <PopoverHeader>Audio</PopoverHeader>
                            <PopoverBody>
                                <Box maxHeight="35vh" overflow="auto">
                                    <PickAudioSource
                                        audioSources={
                                            requestSource.source.audio
                                        }
                                        selected={audioSource}
                                        onChange={(s) => {
                                            onAudioSourceChange(s)
                                            setNested(null)
                                        }}
                                    />
                                </Box>
                            </PopoverBody>
                        </>
                    )}

                    {nested == 'subtitles' && (
                        <>
                            <PopoverHeader>Subtitles</PopoverHeader>
                            <PopoverBody>
                                <Box maxHeight="35vh" overflow="auto">
                                    <PickSubtitleSource
                                        subtitleSources={
                                            requestSource.source.subtitles
                                        }
                                        selected={subtitleSource}
                                        onChange={(s) => {
                                            onSubtitleSourceChange(s)
                                            setNested(null)
                                        }}
                                    />
                                </Box>
                            </PopoverBody>
                        </>
                    )}
                </PopoverContent>
            </Popover>

            {showModal == 'subtitle_offset' && (
                <Modal
                    isOpen={true}
                    onClose={() => setShowModal(null)}
                    portalProps={{ containerRef: containerRef }}
                >
                    <ModalContent
                        backgroundColor="seplis.modalBackgroundColor"
                        maxWidth="800px"
                    >
                        <ModalHeader>Subtitle offset</ModalHeader>
                        <ModalCloseButton />
                        <ModalBody>
                            <PickSubtitleOffset
                                selected={subtitleOffset}
                                onChange={(v) => {
                                    if (v !== null) onSubtitleOffsetChange(v)
                                    else setShowModal(null)
                                }}
                            />
                        </ModalBody>
                    </ModalContent>
                </Modal>
            )}
        </>
    )
}
