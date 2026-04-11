export const ALL_AUDIO_CHANNELS = [2, 6, 8] as const
export type AudioChannels = (typeof ALL_AUDIO_CHANNELS)[number]
