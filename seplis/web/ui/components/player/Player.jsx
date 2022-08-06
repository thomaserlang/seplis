import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'
import {request} from 'api'
import PlayNext from './PlayNext'
import VolumeBar from './VolumeBar'
import AudioSubBar from './AudioSubBar.jsx'
import Resolution from './Resolution.jsx'
import Slider from './Slider.jsx'
import ChromecastIcon from './ChromecastIcon'
import Loader from 'seplis/components/Loader'
import {secondsToTime, guid} from 'seplis/utils'
import './Player.scss'

const propTypes = {
    playServerUrl: PropTypes.string,
    playId: PropTypes.string,
    startTime: PropTypes.number,
    sources: PropTypes.array,
    info: PropTypes.object,
    nextInfo: PropTypes.object,
    backToInfo: PropTypes.object,
    currentInfo: PropTypes.object,
    onAudioChange: PropTypes.func,
    onSubtitleChange: PropTypes.func,
    onResolutionChange: PropTypes.func,
    audio_lang: PropTypes.string,
    subtitle_lang: PropTypes.string,
    onTimeUpdate: PropTypes.func,
}

const defaultProps = {
    startTime: 0,
    info: null,
    nextInfo: null,
}

class Player extends React.Component {

    constructor(props) {
        super(props)
        this.duration = props.sources[0].duration
        this.pingTimer = null
        this.hls = null

        this.volume = 1
        this.hideControlsTimer = null

        this.tracks = []
        this.trackElems = []

        this.setHideControlsTimer()

        this.state = {
            playing: false,
            time: this.props.startTime,
            startTime: this.props.startTime,
            fullscreen: false,
            showControls: true,
            audio: this.props.audio_lang,
            subtitle: this.props.subtitle_lang,
            resolutionWidth: null,
            loading: false,
            source: this.pickSource(),
            showBigPlayButton: false,
            session: guid(),
        }
    }

    componentDidMount() {      
        document.title = `${this.props.currentInfo.title} | SEPLIS`

        this.video.addEventListener('timeupdate', this.onTimeUpdate)
        this.video.addEventListener('pause', this.onPause)
        this.video.addEventListener('play', this.onPlayEvent)  
        this.video.addEventListener('error', this.onPlayError)
        this.video.addEventListener('waiting', this.onPlayWaiting)
        this.video.addEventListener('click', this.onClick)
        this.video.addEventListener('touchstart', this.onClick)
        this.video.addEventListener('loadeddata', this.onLoaded)
        this.video.addEventListener('webkitendfullscreen', this.onFullScreenChange)
        this.video.addEventListener('webkitenterfullscreen', this.onFullScreenChange)      

        document.addEventListener('mousemove', this.onMouseMove)
        document.addEventListener('touchmove', this.onMouseMove)
        document.addEventListener('touchstart', this.onMouseMove)
        document.addEventListener('keydown', this.onKeydown)
        document.addEventListener('beforeunload', this.onBeforeUnload)
        document.addEventListener('fullscreenchange', this.onFullScreenChange)
        document.addEventListener('webkitfullscreenchange', this.onFullScreenChange)
        document.addEventListener('mozfullscreenchange', this.onFullScreenChange)
        document.addEventListener('msfullscreenchange', this.onFullScreenChange)

        this.video.volume = this.volume        
        this.loadStream(this.getPlayUrl())
    }

    componentWillUnmount() {
        clearTimeout(this.pingTimer)
        clearTimeout(this.hideControlsTimer) 

        document.removeEventListener('onmousemove', this.onMouseMove)
        document.removeEventListener('ontouchmove', this.onMouseMove)
        document.removeEventListener('ontouchstart', this.onMouseMove)
        document.removeEventListener('onkeydown', this.onKeydown)
        document.removeEventListener('onbeforeunload', this.onBeforeUnload)
        document.removeEventListener('fullscreenchange', this.onFullScreenChange)
        document.removeEventListener('webkitfullscreenchange', this.onFullScreenChange)
        document.removeEventListener('mozfullscreenchange', this.onFullScreenChange)
        document.removeEventListener('msfullscreenchange', this.onFullScreenChange)
    }

    pickSource() {
        let s = this.props.sources[0]
        for (const source of this.props.sources) {
            if (source.width <= screen.width)
                s = source
        }
        return s
    }

    onLoaded = (e) => {
        this.setState({loading: false})
    }

    loadStream(url) {
        this.setState({loading: true})
        if (this.state.subtitle)
            // Hls.js stalles in the first few seconds if we do not add a timeout for adding the subtitles
            setTimeout(() => { this.setSubtitle(this.state.subtitle) }, 100)
        
        this.setPingTimer()
        
        if (!Hls.isSupported()) {
            this.video.src = url
            this.video.load()
            this.video.play().catch(() => {
                this.setState({showBigPlayButton: true})
            })
            return
        }

        if (this.hls) {
            this.hls.destroy()
            if (this.hls.bufferTimer) {
                clearInterval(this.hls.bufferTimer)
                this.hls.bufferTimer = undefined
            }
            this.hls = null
        }
        this.hls = new Hls({
            startLevel: 0,            
            manifestLoadingTimeOut: 30000,
            maxMaxBufferLength: 3,
            debug: false,
        })
        this.hls.loadSource(url)
        this.hls.attachMedia(this.video)
        this.hls.on(Hls.Events.MANIFEST_PARSED, () => {
            this.video.play().catch(() => {
                this.setState({showBigPlayButton: true})
            })
        })
        this.hls.on(Hls.Events.ERROR, this.onHlsError)
    }

    onHlsError = (event, data) => {
        console.warn(data)
        if (data.fatal) {
            switch(data.type) {
                case Hls.ErrorTypes.NETWORK_ERROR:
                    console.log('hls.js fatal network error encountered, try to recover')
                    this.hls.startLoad()
                    break
                case Hls.ErrorTypes.MEDIA_ERROR:
                    console.log('hls.js fatal media error encountered, try to recover')
                    this.hls.swapAudioCodec()
                    this.handleMediaError()
                    break
                default:
                    console.log('hls.js could not recover')
                    this.hls.destroy()
                    break
            }
        }
    }

    handleMediaError() {
        this.setState({loading: true})
        this.hls.recoverMediaError()
        this.video.play()
    }

    onKeydown = (e) => {
        if (e.code == 'Space')
            this.onPlayPauseClick()
    }

    onClick = (e) => {
        e.preventDefault()
        if (this.video.paused || this.state.loading)
            return
        this.setState({showControls: !this.state.showControls})
    }

    setPingTimer() {
        clearTimeout(this.pingTimer)
        this.pingTimer = setTimeout(() => {
            request(`${this.props.playServerUrl}/keep-alive/${this.state.session}`).catch(e => {
                // if (e.status == 404)
                //    clearTimeout(this.pingTimer)
            })
            this.setPingTimer()
        }, 4000)
    }

    setHideControlsTimer(timeout) {
        if (timeout == undefined)
            timeout = 4000
        clearTimeout(this.hideControlsTimer)
        this.hideControlsTimer = setTimeout(() => {
            this.setState({
                showControls: false,
            })
        }, timeout)
    }

    onMouseMove = (e) => {
        this.setState({
            showControls: true,
        }, () => {            
            this.setHideControlsTimer()
        })
    }

    getPlayUrl() {
        const videoCodecs = this.getSupportedVideoCodecs()
        if (videoCodecs.length == 0) {
            alert('No supported codecs')
            return
        }
        console.log(this.state.source)
        return `${this.props.playServerUrl}/transcode`+
            `?play_id=${this.props.playId}`+
            `&source_index=${this.state.source.index}`+
            `&session=${this.state.session}`+
            `&start_time=${this.state.startTime}`+
            `&audio_lang=${this.state.audio || ''}`+
            `&width=${this.state.resolutionWidth || ''}`+
            `&supported_video_codecs=${String(videoCodecs)}`+
            `&transcode_video_codec=${videoCodecs[0]}`+
            `&client_width=${screen.width}`+
            `&supported_audio_codecs=aac`+
            `&transcode_audio_codec=aac`+
            `&supported_pixel_formats=yuv420p`+
            `&transcode_pixel_format=yuv420p`+
            `&format=hls`
    }

    getSupportedVideoCodecs() {
        const types = {
            //'video/mp4; codecs="hvc1"': 'hevc',
            'video/mp4; codecs="avc1.42E01E"': 'h264',
        }
        const codecs = []
        for (const key in types) {
            if (this.video.canPlayType(key))
                codecs.push(types[key])
        }
        return codecs
    }

    onPlayPauseClick = () => {
        if (this.video.paused) {
            this.video.play()
        } else {
            this.video.pause()
        }
    }

    onFullScreenChange = () => {
        this.setState({
            fullscreen: !!(document.fullScreen || 
                           document.webkitIsFullScreen || 
                           document.mozFullScreen || 
                           document.msFullscreenElement || 
                           document.fullscreenElement),
        })
    }

    onPause = () => {
        this.setState({
            playing: false,
            showControls: true,
        })
    }

    onPlayEvent = () => {
        this.setState({
            playing: true,
            loading: true,
            showBigPlayButton: false,
        })
    }

    onPlayError = (e) => {
        this.setState({loading: false})
        console.warn(e.currentTarget.error)
        if (e.currentTarget.error.code == e.currentTarget.error.MEDIA_ERR_DECODE) {
            this.handleMediaError()
        }
    }

    onPlayWaiting = () => {
        this.setState({loading: true})
    }

    onTimeUpdate = (e) => {
        if (!this.video.paused) {
            this.setState({loading: false})
            let time = this.video.currentTime
            if (this.video.seekable.length <= 1 || this.video.seekable.end(0) <= 1)
                time += this.state.startTime
            this.setState({
                time: time,
                playing: true,
            }, () => {
                if (this.props.onTimeUpdate)
                    this.props.onTimeUpdate(this.state.time, this.state.source.duration)
            })
        }
    }

    changeVideoState(state) {
        state['loading'] = true
        this.setState(state)
        this.cancelPlayUrl()
        this.setState({session: guid()}, () => {
            this.loadStream(this.getPlayUrl())
        })
    }

    onBeforeUnload = () => {
        this.cancelPlayUrl()
    }

    cancelPlayUrl() {
        return new Promise((resolve, reject) => {
            request(
                `${this.props.playServerUrl}/close-session/${this.state.session}`
            ).done(() => {
                resolve()
            }).fail(e => {
                reject(e)
            })
        })
    }

    onFullscreenClick = (event) => {
        if (!this.state.fullscreen) {
            let elem = document.getElementById('player')
            if (elem.enterFullscreen) {
                elem.enterFullscreen()
            } else if (elem.requestFullScreen) {
                elem.requestFullScreen()
            } else if (elem.mozRequestFullScreen) {
                elem.mozRequestFullScreen()
            } else if (elem.webkitRequestFullScreen) {
                elem.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT)
            } else if (elem.webkitEnterFullscreen) {
                elem.webkitEnterFullscreen()
            } else if (this.video.webkitEnterFullscreen) {
                this.video.webkitEnterFullscreen()
            }
        } else {
            if (document.cancelFullScreen) {
                document.cancelFullScreen()
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen()
            } else if (document.webkitCancelFullScreen) {
                document.webkitCancelFullScreen()
            }
        }
        this.setState({fullscreen: !this.state.fullscreen})
    }

    getDurationText() {
        return secondsToTime(parseInt(this.duration))
    }

    getCurrentTimeText() {
        return secondsToTime(parseInt(this.state.time))
    }

    renderPlayNext() {
        if (!this.props.nextInfo) return
        return (
            <PlayNext
                title={this.props.nextInfo.title}
                url={this.props.nextInfo.url}
            />    
        )
    }

    onVolumeChange = (volume) => {
        this.volume = volume
        if (this.video)
            this.video.volume = volume
    }

    onAudioChange = (lang) => {
        if (this.props.onAudioChange)
            this.props.onAudioChange(lang)
        this.changeVideoState({
            audio: lang,
            startTime: this.state.time,
        })
    }

    onSubtitleChange = (lang) => {
        if (this.props.onSubtitleChange)
            this.props.onSubtitleChange(lang)
        this.setState({subtitle: lang}, () => {
            this.setSubtitle(lang)
        })
    }

    setSubtitle(lang) {
        for (let i = this.tracks.length - 1; i >= 0; i--) {
            this.tracks[i].mode = 'disabled'
            this.trackElems[i].remove()
            this.trackElems.pop()
            this.tracks.pop()
        }

        const track = document.createElement('track')
        track.kind = 'subtitles'
        track.src = `${this.props.playServerUrl}/subtitle-file`+
            `?play_id=${this.props.playId}`+
            `&start_time=${this.state.startTime}`+
            `&source_index=${this.state.source.index}`+
            `&lang=${lang}`
        track.track.mode = 'hidden'
        track.track.addEventListener('cuechange', this.onCueChange)
        track.addEventListener('load', (e) => {
            e.target.track.mode = 'showing'
        }, false)
        this.tracks.push(track.track)
        this.trackElems.push(track)
        this.video.appendChild(track)
    }

    onCueChange = (e) => {
        const cues = e.currentTarget.cues;
        for (let i = 0; i < cues.length; i++) {
            cues[i].line = -3
        }   
    }

    onResolutionChange = (width, source) => {
        if (this.props.onResolutionChange)
            this.props.onResolutionChange(width, source)
        this.changeVideoState({
            resolutionWidth: width,
            source: source,
        })
    }

    onSliderNewTime = (newTime) => {
        this.video.pause()
        this.setHideControlsTimer()
        this.changeVideoState({
            time: newTime,
            startTime: newTime,
        })
    }

    onSliderReturnCurrentTime = () => {
        return this.state.time
    }

    showControlsVisibility() {
        return ((!this.state.showControls) && (this.state.playing))?'hidden':'visible'
    }

    renderControlsTop() {
        return (
            <div 
                className="controls controls-top" 
                style={{visibility: this.showControlsVisibility()}}
            >
                <div className="control">
                    <a 
                        className="fas fa-times" 
                        href={this.props.backToInfo.url}
                        title={this.props.backToInfo.title}
                    />
                </div>
                <div className="control-text control-text-title">
                    {this.props.currentInfo.title}
                </div>
                <div className="control-spacer" />
                <div className="control">
                    <Resolution 
                        sources={this.props.sources} 
                        selectedSource={this.state.source}
                        onResolutionChange={this.onResolutionChange}
                    />
                </div>
                <div className="control">
                    <ChromecastIcon />
                </div>
                <div className="control">
                    <AudioSubBar 
                        source={this.state.source} 
                        onAudioChange={this.onAudioChange}
                        onSubtitleChange={this.onSubtitleChange}
                    />
                </div>
                <div className="control">
                    <VolumeBar onChange={this.onVolumeChange} />
                </div>
                <div className="control">
                    {this.renderPlayNext()}
                </div>
            </div>
        )
    }

    renderControlsBottom() {
        let playPause = ClassNames({
            fa: true,
            'fa-pause': this.state.playing,
            'fa-play': !this.state.playing,
        })
        let fullscreen = ClassNames({
            fa: true,
            'fa-expand': this.state.fullscreen,
            'fa-arrows-alt': !this.state.fullscreen,
        })
        return (
            <div 
                className="controls" 
                style={{visibility: this.showControlsVisibility()}}
            >
                <div className="control">
                    <span 
                        className={playPause}
                        onClick={this.onPlayPauseClick}
                    >
                    </span>
                </div>
                <div className="control-text">
                    {this.getCurrentTimeText()}
                </div>
                <Slider 
                    duration={this.duration}
                    onReturnCurrentTime={this.onSliderReturnCurrentTime}
                    onNewTime={this.onSliderNewTime}
                />
                <div className="control-text" title="Timeleft">
                    {this.getDurationText()}
                </div>
                <div className="control">
                    <span 
                        className={fullscreen}
                        onClick={this.onFullscreenClick}
                    >
                    </span>
                </div>
            </div>
        )
    }

    renderLoading() {
        if (!this.state.loading)
            return null
        return <Loader hcenter={true} />
    }

    renderBigPlayButton() {
        if ((this.state.showBigPlayButton) && !this.state.loading)
            return <big-play-button onClick={this.onPlayPauseClick}>
                <i className="fa fa-play" />
            </big-play-button>
    }

    render() {
        return (
            <div id="player">  
                <div className="overlay">
                    <video 
                        className="video" 
                        preload="none" 
                        autoPlay={false}
                        controls={false}
                        crossOrigin="anonymous"
                        ref={(ref) => this.video = ref}
                    />
                    {this.renderControlsTop()}
                    {this.renderControlsBottom()}
                    {this.renderLoading()}
                    {this.renderBigPlayButton()}
                </div>
            </div>
        )
    }
}
Player.propTypes = propTypes
Player.defaultProps = defaultProps
export default Player

export function getPlayServer(url) {
    /* `url` must be a url to the play servers. 
        Example: /1/shows/1/episodes/1/play-servers.
        Returns a promise.
    */
    return new Promise((resolve, reject) => {
        request(
            url
        ).done(playServers => {
            var selected = false
            var i = 0
            if (playServers.length == 0) {
                reject({code: 1, message: 'No play servers.'})
                return
            }
            for (var s of playServers) {
                i += 1
                request(s.play_url+'/sources', {
                    query: {
                        play_id: s.play_id,
                    }
                }).done(sources => {
                    if (selected) 
                        return
                    selected = true
                    resolve({
                        playServer: s, 
                        sources: sources,
                    })
                }).always(() => {
                    i -= 1
                    if ((i == 0) && (selected == false)) {
                        reject({code: 2, message: 'This episode is not on any of your play servers.'})
                    }
                })
            }
        }).fail((e) => {
            reject(e)
        })
    })
}