import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import ky from 'ky'
import { PlayRequestSource, PlayServerMedia } from '../types/play-source.types'
import {
    getSupportedAudioCodecs,
    getSupportedVideoCodecs,
    getSupportedVideoContainers,
} from '../utils/video.utils'

export interface PlayServerMediaGetProps extends ApiHelperProps<{}> {
    playRequestSource: PlayRequestSource
    startTime?: number
    audio?: string
    maxBitrate?: number
    forceTranscode?: boolean
    maxAudioChannels?: number
    supportedVideoCodecs?: string[]
    supportedAudioCodecs?: string[]
    transcodeVideoCodec?: string
    transcodeAudioCodec?: string
    supportedVideoContainers?: string[]
}

export const {
    get: getPlayServerMedia,
    useGet: useGetPlayServerMedia,
    queryKey: playServerMediaQueryKey,
} = useApiHelper<PlayServerMedia, PlayServerMediaGetProps>({
    url: () => '',
    queryKey: (props) =>
        [
            'play-server-media',
            props.playRequestSource.request.play_id,
            props.startTime,
            props.audio,
            props.maxBitrate,
            props.forceTranscode,
            props.maxAudioChannels,
            props.supportedVideoCodecs,
            props.supportedAudioCodecs,
            props.transcodeVideoCodec,
            props.transcodeAudioCodec,
            props.supportedVideoContainers,
        ].filter((x) => x !== undefined),
    getFn: async ({
        playRequestSource,
        startTime,
        audio,
        maxBitrate,
        forceTranscode = false,
        maxAudioChannels = 6,
        supportedVideoCodecs,
        supportedAudioCodecs,
        transcodeVideoCodec,
        transcodeAudioCodec,
        supportedVideoContainers,
        signal,
    }) => {
        const videoCodecs = supportedVideoCodecs ?? getSupportedVideoCodecs()
        if (videoCodecs.length === 0) throw new Error('No supported codecs')

        const audioCodecs = supportedAudioCodecs ?? getSupportedAudioCodecs()
        const videoContainers =
            supportedVideoContainers ?? getSupportedVideoContainers()
        const videoTranscodeCodec = transcodeVideoCodec ?? videoCodecs[0]
        const audioTranscodeCodec = transcodeAudioCodec ?? 'aac'

        const r = await ky.get<PlayServerMedia>(
            `${playRequestSource.request.play_url}/request-media`,
            {
                signal,
                searchParams: Object.fromEntries(
                    Object.entries({
                        play_id: playRequestSource.request.play_id,
                        source_index: playRequestSource.source.index,
                        start_time: startTime || 0,
                        audio_lang: audio,
                        max_video_bitrate: maxBitrate,
                        supported_video_codecs: String(videoCodecs),
                        transcode_video_codec: videoTranscodeCodec,
                        supported_audio_codecs: String(audioCodecs),
                        transcode_audio_codec: audioTranscodeCodec,
                        format: 'hls',
                        max_audio_channels: maxAudioChannels,
                        supported_video_containers: String(videoContainers),
                        force_transcode: forceTranscode ? 'true' : 'false',
                    }).filter(
                        ([, value]) => value !== undefined && value !== null,
                    ),
                ),
            },
        )
        const data = await r.json()
        if (data.hls_url.startsWith('/')) {
            data.hls_url = playRequestSource.request.play_url + data.hls_url
            data.direct_play_url =
                playRequestSource.request.play_url + data.direct_play_url
            data.keep_alive_url =
                playRequestSource.request.play_url + data.keep_alive_url
            data.close_session_url =
                playRequestSource.request.play_url + data.close_session_url
        }
        return data
    },
})
