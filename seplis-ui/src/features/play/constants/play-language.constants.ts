import { getBrowserPreferredLangs } from '../utils/play-source.utils'

export const PREFERRED_AUDIO_LANGS: string[] = [
    'jpa',
    'eng',
    ...getBrowserPreferredLangs(),
]
export const PREFERRED_SUBTITLE_LANGS: string[] = [
    ...getBrowserPreferredLangs(),
    'eng',
]
