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
}

export const {
    get: getPlayServerMedia,
    useGet: useGetPlayServerMedia,
    queryKey: playServerMediaQueryKey,
} = useApiHelper<PlayServerMedia, PlayServerMediaGetProps>({
    url: () => '',
    queryKey: (props) => ['play-server-media', { ...props }],
    getFn: async ({
        playRequestSource,
        startTime,
        audio,
        maxBitrate,
        forceTranscode = false,
        maxAudioChannels = 6,
    }) => {
        const videoCodecs = getSupportedVideoCodecs()
        if (videoCodecs.length == 0) throw new Error('No supported codecs')

        const r = await ky.get<PlayServerMedia>(
            `${playRequestSource.request.play_url}/request-media`,
            {
                searchParams: Object.fromEntries(
                    Object.entries({
                        play_id: playRequestSource.request.play_id,
                        source_index: playRequestSource.source.index,
                        start_time: startTime || 0,
                        audio_lang: audio,
                        max_video_bitrate: maxBitrate,
                        supported_video_codecs: String(videoCodecs),
                        transcode_video_codec: videoCodecs[0],
                        supported_audio_codecs: String(getSupportedAudioCodecs()),
                        transcode_audio_codec: 'aac',
                        format: 'hls',
                        max_audio_channels: maxAudioChannels,
                        supported_video_containers: String(
                            getSupportedVideoContainers(),
                        ),
                        force_transcode: forceTranscode ? 'true' : 'false',
                    }).filter(([, value]) => value !== undefined && value !== null),
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
