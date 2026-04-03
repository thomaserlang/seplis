export function langCodeToLang(code: string) {
    try {
        return new Intl.DisplayNames(['en'], { type: 'language' }).of(code)
    } catch (e) {
        return code
    }
}
