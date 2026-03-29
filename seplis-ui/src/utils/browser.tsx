import { detect } from 'detect-browser'
import mobile from 'is-mobile'

export const browser = detect()

export const isMobile = mobile()