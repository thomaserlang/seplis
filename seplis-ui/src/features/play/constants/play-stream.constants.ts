export const ALL_STREAM_FORMATS = ['hls'] as const
export type StreamFormat = (typeof ALL_STREAM_FORMATS)[number]
