export function getSupportedVideoCodecs() {
    const video = document.createElement('video')
    const types: { [key: string]: string } = {
        'video/mp4; codecs="hvc1"': 'hevc',
        'video/mp4; codecs="hev1.1.6.L93.90"': 'hevc',
        'video/mp4; codecs="avc1.42E01E"': 'h264',
        'video/mp4; codecs="av01.0.08M.08"': 'av1',
    }
    const codecs: string[] = []
    for (const key in types) if (video.canPlayType(key)) codecs.push(types[key])
    return [...new Set(codecs)]
}

export function getSupportedVideoContainers() {
    const video = document.createElement('video')
    const containers: { [key: string]: string } = {
        'video/webm': 'webm',
        'video/mp4': 'mp4',
    }
    return Object.entries(containers)
        .filter(([mime]) => video.canPlayType(mime))
        .map(([, name]) => name)
}

export function getSupportedAudioCodecs() {
    const video = document.createElement('video')
    const types: { [key: string]: string } = {
        'audio/aac': 'aac',
        'audio/mp4; codecs="ec-3"': 'eac3',
        'audio/mp4; codecs="ac-3"': 'ac3',
        'audio/mp4; codecs="ac-4"': 'ac4',
        'audio/mp4; codecs="opus"': 'opus',
        'audio/mp4; codecs="flac"': 'flac',
        'audio/mp4; codecs="dtsc"': 'dtsc',
        'audio/mp4; codecs="dtse"': 'dtse',
        'audio/mp4; codecs="dtsx"': 'dtsx',
    }
    const codecs: string[] = []
    for (const key in types) if (video.canPlayType(key)) codecs.push(types[key])
    return [...new Set(codecs)]
}
