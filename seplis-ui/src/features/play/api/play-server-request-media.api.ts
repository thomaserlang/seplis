import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import ky from 'ky'
import { HDRType } from '../types/media.types'
import { PlayRequestSource, PlayServerMedia } from '../types/play-source.types'
import { recommendResolution } from '../utils/play-resolution.utils'

export interface PlayServerMediaGetProps extends ApiHelperProps<{}> {
    playRequestSource: PlayRequestSource
    startTime?: number
    audio?: string
    maxBitrate?: number
    forceTranscode?: boolean
    maxAudioChannels: number
    supportedVideoCodecs: string[]
    supportedAudioCodecs: string[]
    transcodeVideoCodec: string
    transcodeAudioCodec: string
    supportedVideoContainers: string[]
    format: string
    supportedHdrFormats: HDRType[]
    hdrEnabled: boolean
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
            props.format,
            props.supportedHdrFormats,
            props.hdrEnabled,
        ].filter((x) => x !== undefined),
    getFn: async ({
        playRequestSource,
        startTime,
        audio,
        maxBitrate,
        forceTranscode = false,
        maxAudioChannels,
        supportedVideoCodecs,
        supportedAudioCodecs,
        transcodeVideoCodec,
        transcodeAudioCodec,
        supportedVideoContainers,
        format,
        supportedHdrFormats,
        hdrEnabled,
        signal,
    }) => {
        if (supportedVideoCodecs.length === 0)
            throw new Error('No supported video codecs')

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
                        supported_video_codecs: String(supportedVideoCodecs),
                        transcode_video_codec: transcodeVideoCodec,
                        supported_audio_codecs: String(supportedAudioCodecs),
                        transcode_audio_codec: transcodeAudioCodec,
                        format,
                        max_audio_channels: maxAudioChannels,
                        supported_video_containers: String(
                            supportedVideoContainers,
                        ),
                        force_transcode: forceTranscode ? 'true' : 'false',
                        max_width: maxBitrate
                            ? recommendResolution(
                                  maxBitrate,
                                  transcodeVideoCodec,
                              )
                            : undefined,
                        // TODO: bug on the play server preventing multiple HDR formats to be sent
                        supported_hdr_formats:
                            hdrEnabled && supportedHdrFormats?.length
                                ? supportedHdrFormats[0]
                                : undefined,
                    }).filter(
                        ([, value]) => value !== undefined && value !== null,
                    ) as [string, string | number | boolean][],
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
