import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'
import {request} from 'api'
import PlayNext from './PlayNext'
import VolumeBar from './VolumeBar'
import AudioSubBar from './AudioSubBar.jsx'
import Slider from './Slider.jsx'
import ChromecastIcon from './ChromecastIcon'
import Loader from 'seplis/components/Loader'
import {secondsToTime} from 'utils'
import './Player.scss'

const propTypes = {
    playServerUrl: PropTypes.string,
    playId: PropTypes.string,
    session: PropTypes.string,
    startTime: PropTypes.number,
    metadata: PropTypes.object,
    info: PropTypes.object,
    nextInfo: PropTypes.object,
    backToInfo: PropTypes.object,
    currentInfo: PropTypes.object,
    onAudioChange: PropTypes.func,
    onSubtitleChange: PropTypes.func,
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
        this.onPlayPauseClick = this.playPauseClick.bind(this)
        this.duration = parseInt(props.metadata.format.duration)
        this.pingTimer = null
        this.hls = null
        this.onFullscreenClick = this.fullscreenClick.bind(this)
        this.onVolumeChange = this.volumeChange.bind(this)

        this.onAudioChange = this.audioChange.bind(this)
        this.onSubtitleChange = this.subtitleChange.bind(this)

        this.volume = 1
        this.hideControlsTimer = null

        this.onSliderReturnCurrentTime = this.sliderReturnCurrentTime.bind(this)
        this.onSliderNewTime = this.sliderNewTime.bind(this)
        this.setHideControlsTimer()

        this.state = {
            playing: false,
            time: this.props.startTime,
            startTime: this.props.startTime,
            session: props.session,
            fullscreen: false,
            showControls: true,
            audio: this.props.audio_lang,
            subtitle: this.props.subtitle_lang,
            loading: false,
        }
    }

    componentDidMount() {      
        document.title = `${this.props.currentInfo.title} | SEPLIS`

        this.video.addEventListener('timeupdate', this.timeupdateEvent.bind(this))
        this.video.addEventListener('pause', this.pauseEvent.bind(this))
        this.video.addEventListener('play', this.playEvent.bind(this))
        
        document.addEventListener('fullscreenchange', this.fullscreenchangeEvent.bind(this))
        document.addEventListener('webkitfullscreenchange', this.fullscreenchangeEvent.bind(this))
        this.video.addEventListener('webkitendfullscreen', this.fullscreenchangeEvent.bind(this))
        this.video.addEventListener('webkitenterfullscreen', this.fullscreenchangeEvent.bind(this))
        document.addEventListener('mozfullscreenchange', this.fullscreenchangeEvent.bind(this))
        document.addEventListener('msfullscreenchange', this.fullscreenchangeEvent.bind(this))
        
        this.video.addEventListener('error', this.playError.bind(this))
        this.video.addEventListener('waiting', this.playWaiting.bind(this))
        this.video.addEventListener('click', this.playClick.bind(this))
        this.video.addEventListener('touchstart', this.playClick.bind(this))
        this.video.addEventListener('loadeddata', this.loadedEvent.bind(this))
        this.setPingTimer()
        this.video.volume = this.volume
        
        this.loadStream(this.getPlayUrl())

        document.onmousemove = this.mouseMove.bind(this)
        document.ontouchmove = this.mouseMove.bind(this)
        document.onkeypress = this.keypress.bind(this)
        document.onbeforeunload = this.beforeUnload.bind(this)
    }

    componentWillUnmount() {
        clearTimeout(this.pingTimer)
        clearTimeout(this.hideControlsTimer)
    }

    loadedEvent(e) {
        this.setState({loading: false})
    }

    loadStream(url) {
        this.setState({loading: true})
        if (!Hls.isSupported()) {
            this.video.src = url
            this.video.load()
            this.video.play()
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
            debug: false,
        })
        this.hls.loadSource(url)
        this.hls.attachMedia(this.video)
        this.hls.on(Hls.Events.MANIFEST_PARSED, () => {
            this.video.play()
        })
        this.hls.on(Hls.Events.ERROR, this.hlsError.bind(this))
    }

    hlsError(event, data) {
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

    keypress(e) {
        if (e.code == 'Space')
            this.playPauseClick()
    }

    playClick(e) {
        e.preventDefault()
        if (this.video.paused || this.state.loading)
            return
        this.setState({showControls: !this.state.showControls})
    }

    setPingTimer() {
        clearTimeout(this.pingTimer)
        this.pingTimer = setTimeout(() => {
            request(this.getPlayUrl()+'&action=ping')
            this.setPingTimer()
        }, 2000)
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

    mouseMove(e) {
        this.setState({
            showControls: true,
        })
        this.setHideControlsTimer()
    }

    getPlayUrl() {
        let s = `${this.props.playServerUrl}/play`+
            `?play_id=${this.props.playId}`+
            `&session=${this.props.session}`+
            `&start_time=${this.state.startTime}`+
            `&subtitle_lang=${this.state.subtitle || ''}`+
            `&audio_lang=${this.state.audio || ''}`
        return s
    }

    playPauseClick() {
        if (this.video.paused) {
            this.video.play()
        } else {
            this.video.pause()
        }
    }

    fullscreenchangeEvent() {
        this.setState({
            fullscreen: !!(document.fullScreen || 
                           document.webkitIsFullScreen || 
                           document.mozFullScreen || 
                           document.msFullscreenElement || 
                           document.fullscreenElement),
        })
    }

    pauseEvent() {
        this.setState({
            playing: false,
            showControls: true,
        })
    }

    playEvent() {
        this.setState({
            playing: true,
            loading: true,
        })
    }

    playError(e) {
        this.setState({loading: false})
        console.warn(e.currentTarget.error)
        if (e.currentTarget.error.code == e.currentTarget.error.MEDIA_ERR_DECODE) {
            this.handleMediaError()
        }
    }

    playWaiting() {
        this.setState({loading: true})
    }

    timeupdateEvent(e) {
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
                    this.props.onTimeUpdate(this.state.time)
            })
        }
    }

    changeVideoState(state) {
        state['loading'] = true
        this.setState(state)
        this.cancelPlayUrl().then(() => {
            this.loadStream(this.getPlayUrl())
            this.setPingTimer()
        })
    }

    beforeUnload() {
        this.cancelPlayUrl()
    }

    cancelPlayUrl() {
        return new Promise((resolve, reject) => {
            request(
                this.getPlayUrl()+'&action=cancel'
            ).done(() => {
                resolve()
            }).fail(e => {
                reject(e)
            })
        })
    }

    fullscreenClick(event) {
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

    volumeChange(volume) {
        this.volume = volume
        if (this.video)
            this.video.volume = volume
    }

    audioChange(lang) {
        if (this.props.onAudioChange)
            this.props.onAudioChange(lang)
        this.changeVideoState({
            audio: lang,
            startTime: this.state.time,
        })
    }

    subtitleChange(lang) {
        if (this.props.onSubtitleChange)
            this.props.onSubtitleChange(lang)
        this.changeVideoState({
            subtitle: lang,
            startTime: this.state.time,
        })
    }

    sliderNewTime(newTime) {
        this.video.pause()
        this.setHideControlsTimer()
        this.changeVideoState({
            time: newTime,
            startTime: newTime,
        })
    }

    sliderReturnCurrentTime() {
        return this.state.time
    }

    showControlsVisibility() {
        return this.state.showControls?'visible':'hidden'
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
                    <ChromecastIcon />
                </div>
                <div className="control">
                    <AudioSubBar 
                        metadata={this.props.metadata} 
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

    render() {
        return (
            <div id="player">  
                <div className="overlay">
                    <video 
                        className="video" 
                        preload="none" 
                        autoPlay={false}
                        controls={false}
                        ref={(ref) => this.video = ref}
                    />
                    {this.renderControlsTop()}
                    {this.renderControlsBottom()}
                    {this.renderLoading()}
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
                request(s.play_url+'/metadata', {
                    query: {
                        play_id: s.play_id,
                    }
                }).done(metadata => {
                    if (selected) 
                        return
                    selected = true
                    resolve({
                        playServer: s, 
                        metadata: metadata,
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