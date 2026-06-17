import type {
    PlayRequestSource,
    PlaySourceStream,
} from '@/features/play/types/play-source.types'
import { toLangKey } from '@/features/play/utils/play-source.utils'
import type { SeplisCastMediaIdentity } from './chromecast-media-identity'

interface CreateChromecastLoadRequestProps {
    source: PlayRequestSource
    contentUrl: string
    directPlayContentType?: string
    title?: string
    secondaryTitle?: string
    subtitle?: PlaySourceStream
    currentTime: number
    seplisCastIdentity: SeplisCastMediaIdentity
    customData: Record<string, unknown>
}

export function getSubtitleTrackIds(
    subtitles: PlaySourceStream[],
    subtitle?: PlaySourceStream,
) {
    if (!subtitle) return []

    const idx = subtitles.findIndex(
        (s) => s.group_index === subtitle.group_index,
    )
    return idx >= 0 ? [idx + 1] : []
}

function createSubtitleTracks(source: PlayRequestSource) {
    return source.source.subtitles.map((sub, i) => {
        const key = toLangKey(sub)
        const subtitleUrl =
            `${source.request.play_url}/subtitle-file` +
            `?play_id=${source.request.play_id}` +
            `&source_index=${source.source.index}` +
            `&lang=${key}`
        const track = new chrome.cast.media.Track(
            i + 1,
            chrome.cast.media.TrackType.TEXT,
        )
        track.trackContentId = subtitleUrl
        track.trackContentType = 'text/vtt'
        track.subtype = chrome.cast.media.TextTrackType.SUBTITLES
        track.name = sub.title || sub.language
        track.language = sub.language
        return track
    })
}

function applyHlsSegmentFormat(mediaInfo: chrome.cast.media.MediaInfo) {
    const media = chrome.cast.media as unknown as {
        HlsVideoSegmentFormat?: { FMP4?: unknown }
        HlsSegmentFormat?: { FMP4?: unknown }
    }
    const fmp4SegmentFormat =
        media.HlsVideoSegmentFormat?.FMP4 ?? media.HlsSegmentFormat?.FMP4

    if (fmp4SegmentFormat != null) {
        ;(
            mediaInfo as chrome.cast.media.MediaInfo & {
                hlsVideoSegmentFormat?: unknown
            }
        ).hlsVideoSegmentFormat = fmp4SegmentFormat
    }
}

export function createChromecastLoadRequest({
    source,
    contentUrl,
    directPlayContentType,
    title,
    secondaryTitle,
    subtitle,
    currentTime,
    seplisCastIdentity,
    customData,
}: CreateChromecastLoadRequestProps) {
    const metadata = new chrome.cast.media.GenericMediaMetadata()
    metadata.title = title ?? ''
    metadata.subtitle = secondaryTitle ?? ''

    const mediaInfo = new chrome.cast.media.MediaInfo(
        contentUrl,
        directPlayContentType ?? 'application/x-mpegurl',
    )
    if (!directPlayContentType) applyHlsSegmentFormat(mediaInfo)
    ;(mediaInfo as any).contentUrl = contentUrl
    mediaInfo.streamType = chrome.cast.media.StreamType.BUFFERED
    mediaInfo.metadata = metadata
    mediaInfo.duration = source.source.duration
    mediaInfo.tracks = createSubtitleTracks(source)
    mediaInfo.customData = {
        seplis: seplisCastIdentity,
    }

    const request = new chrome.cast.media.LoadRequest(mediaInfo)
    request.autoplay = true
    request.currentTime = currentTime

    const activeTrackIds = getSubtitleTrackIds(
        source.source.subtitles,
        subtitle,
    )
    if (activeTrackIds.length > 0) request.activeTrackIds = activeTrackIds

    request.customData = {
        seplis: seplisCastIdentity,
        ...customData,
    }

    return request
}
