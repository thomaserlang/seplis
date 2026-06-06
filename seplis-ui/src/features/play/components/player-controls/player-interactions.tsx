import { Hotkey, MediaGesture } from '@videojs/react'

export function PlayerVideoInteractions() {
    return (
        <>
            <Hotkey keys="Space" action="togglePaused" target="document" />
            <Hotkey keys="k" action="togglePaused" target="document" />
            <Hotkey keys="m" action="toggleMuted" target="document" />
            <Hotkey keys="f" action="toggleFullscreen" target="document" />
            <Hotkey keys="c" action="toggleSubtitles" target="document" />
            <Hotkey
                keys="i"
                action="togglePictureInPicture"
                target="document"
            />
            <Hotkey keys="ArrowRight" action="seekStep" value={5} />
            <Hotkey keys="ArrowLeft" action="seekStep" value={-5} />
            <Hotkey keys="l" action="seekStep" value={10} />
            <Hotkey keys="j" action="seekStep" value={-10} />
            <Hotkey keys="ArrowUp" action="volumeStep" value={0.05} />
            <Hotkey keys="ArrowDown" action="volumeStep" value={-0.05} />
            <Hotkey keys="0-9" action="seekToPercent" target="document" />
            <Hotkey
                keys="Home"
                action="seekToPercent"
                value={0}
                target="document"
            />
            <Hotkey
                keys="End"
                action="seekToPercent"
                value={100}
                target="document"
            />
            <Hotkey keys=">" action="speedUp" target="document" />
            <Hotkey keys="<" action="speedDown" target="document" />

            <MediaGesture
                type="tap"
                action="togglePaused"
                pointer="mouse"
                region="center"
            />
            <MediaGesture type="tap" action="toggleControls" pointer="touch" />
            <MediaGesture
                type="doubletap"
                action="seekStep"
                value={-10}
                region="left"
            />
            <MediaGesture
                type="doubletap"
                action="toggleFullscreen"
                region="center"
            />
            <MediaGesture
                type="doubletap"
                action="seekStep"
                value={10}
                region="right"
            />
        </>
    )
}
