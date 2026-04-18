import { MediaGesture, MediaHotkey } from '@videojs/react'

export function PlayerVideoInteractions() {
    return (
        <>
            <MediaHotkey keys="Space" action="togglePaused" target="document" />
            <MediaHotkey keys="k" action="togglePaused" target="document" />
            <MediaHotkey keys="m" action="toggleMuted" target="document" />
            <MediaHotkey keys="f" action="toggleFullscreen" target="document" />
            <MediaHotkey keys="c" action="toggleSubtitles" target="document" />
            <MediaHotkey
                keys="i"
                action="togglePictureInPicture"
                target="document"
            />
            <MediaHotkey keys="ArrowRight" action="seekStep" value={5} />
            <MediaHotkey keys="ArrowLeft" action="seekStep" value={-5} />
            <MediaHotkey keys="l" action="seekStep" value={10} />
            <MediaHotkey keys="j" action="seekStep" value={-10} />
            <MediaHotkey keys="ArrowUp" action="volumeStep" value={0.05} />
            <MediaHotkey keys="ArrowDown" action="volumeStep" value={-0.05} />
            <MediaHotkey keys="0-9" action="seekToPercent" target="document" />
            <MediaHotkey
                keys="Home"
                action="seekToPercent"
                value={0}
                target="document"
            />
            <MediaHotkey
                keys="End"
                action="seekToPercent"
                value={100}
                target="document"
            />
            <MediaHotkey keys=">" action="speedUp" target="document" />
            <MediaHotkey keys="<" action="speedDown" target="document" />

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
