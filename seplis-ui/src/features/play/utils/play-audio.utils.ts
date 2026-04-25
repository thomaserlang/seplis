export function audioChannelLabel(n: number): string {
    if (n === 2) return '2ch (Stereo)'
    if (n === 6) return '6ch (5.1)'
    if (n === 8) return '8ch (7.1)'
    return `${n}ch`
}
