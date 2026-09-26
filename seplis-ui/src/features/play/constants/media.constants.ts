export const HDR_FORMATS = ['hdr10', 'hlg', 'dovi'] as const
export const HDR_FORMAT_LABELS = {
    hdr10: 'HDR10',
    hlg: 'HLG',
    dovi: 'Dolby Vision',
} satisfies Record<(typeof HDR_FORMATS)[number], string>

export const VIDEO_CODECS = ['av1', 'h264', 'hevc'] as const
export const VIDEO_CODEC_LABELS = {
    av1: 'AV1',
    h264: 'H.264',
    hevc: 'H.265 / HEVC',
} satisfies Record<(typeof VIDEO_CODECS)[number], string>

export const AUDIO_CODECS = [
    'aac',
    'eac3',
    'ac3',
    'ac4',
    'opus',
    'flac',
    'dts',
    'mp3',
] as const
export const AUDIO_CODEC_LABELS = {
    aac: 'AAC',
    eac3: 'DD+',
    ac3: 'Dolby Digital',
    ac4: 'Dolby AC-4',
    opus: 'Opus',
    flac: 'FLAC',
    dts: 'DTS',
    mp3: 'MP3',
} satisfies Record<(typeof AUDIO_CODECS)[number], string>

export const TRANSCODE_AUDIO_CODECS = ['aac', 'opus', 'flac', 'mp3'] as const

export const AUDIO_CODEC_CHECK_TYPES = {
    aac: ['audio/mp4; codecs="mp4a.40.2"', 'audio/aac'],
    eac3: ['audio/mp4; codecs="ec-3"', 'audio/eac3'],
    ac3: ['audio/mp4; codecs="ac-3"', 'audio/ac3'],
    ac4: ['audio/mp4; codecs="ac-4"'],
    opus: ['audio/mp4; codecs="opus"'],
    flac: ['audio/mp4; codecs="fLaC"', 'audio/flac'],
    dts: [
        'audio/mp4; codecs="dtsc"',
        'audio/mp4; codecs="dtse"',
        'audio/mp4; codecs="dtsx"',
    ],
    mp3: ['audio/mp4; codecs="mp4a.40.34"', 'audio/mpeg'],
} as const satisfies Record<(typeof AUDIO_CODECS)[number], readonly string[]>

export const VIDEO_CONTAINERS = ['mp4', 'webm'] as const

export const STREAM_FORMATS = ['hls'] as const

export const AUDIO_CHANNELS = [2, 6, 8] as const
