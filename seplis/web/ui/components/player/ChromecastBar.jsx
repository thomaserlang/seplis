import React from 'react'
import ClassNames from 'classnames'
import Chromecast from './Chromecast'
import Slider from './Slider'
import Settings from './Settings'
import {episodeTitle, secondsToTime} from 'utils'
import {request} from 'api'
import {trigger_episode_watched_status} from 'seplis/events'

import './ChromecastBar.scss'
import './Player.scss'

class ChromecastBar extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            connected: false,
            deviceName: "",
            playerState: '',
            info: null,
            currentTime: 0,
            loading: false,
            changingTime: false,
        }
        this.cast = null

        this.onSliderReturnCurrentTime = this.sliderReturnCurrentTime.bind(this)
        this.onSliderNewTime = this.sliderNewTime.bind(this)
        this.onPlayPauseClick = this.playPauseClick.bind(this)
        this.clickPlayNextEpisode = this.playNextEpisode.bind(this)
    }

    componentDidMount() {
        this.cast = new Chromecast()
        this.cast.load(this.initCast.bind(this))
    }

    componentWillUnmount() {
        this.cast.removeEventListener(
            'anyChanged',
            this.castStateChanged.bind(this)
        )
        const session = this.cast.getSession()
        if (session) {
            session.removeMessageListener(
                'urn:x-cast:net.seplis.cast.get_custom_data',
                this.receiveCastInfo.bind(this),
            )
        }
    }

    onAudioChange = (lang) => {
        if (lang == '')
            lang = null
        this.subAudioSubSave({audio_lang: lang})
    }    

    onSubtitleChange = (lang) => {
        if (lang == '')
            lang = null
        this.subAudioSubSave({subtitle_lang: lang})
    }
    
    subAudioSubSave(data) {
        if (this.state.info.type == 'episode') {
            const show = this.state.info.series
            const episode = this.state.info.episode
            request(`/1/shows/${show.id}/user-subtitle-lang`, {
                method: 'PATCH',
                data: data,
            }).done(() => {
                this.cast.playEpisode(
                    show.id, 
                    episode.number, 
                    this.state.currentTime, 
                    this.state.info.selectedSource.index,
                    this.state.info.subtitleOffset,
                )
            }).catch((e) => {
                alert(e.message)
            })
        } else {
            this.cast.playMovie(
                this.state.info.movie.id, 
                this.state.currentTime, 
                this.state.info.selectedSource.index, 
                data.audio_lang || this.state.info.audioLang, 
                data.subtitle_lang || this.state.info.subtitleLang,
                this.state.info.subtitleOffset,
            )
        }
    }

    onResolutionChange = (width, source) => {
        if (this.state.info.type == 'episode') {
            this.cast.playEpisode(
                this.state.info.series.id, 
                this.state.info.episode.number, 
                this.state.currentTime, 
                source.index,
                this.state.info.subtitleOffset,
            )
        } else {
            this.cast.playMovie(
                this.state.info.movie.id, 
                this.state.currentTime, 
                source.index, 
                this.state.info.audioLang,
                this.state.info.subtitleLang,
                this.state.info.subtitleOffset,
            )
        }
    }

    onSubtitleOffsetChange = (seconds) => {
        if (this.state.info.type == 'episode') {
            this.cast.playEpisode(
                this.state.info.series.id, 
                this.state.info.episode.number, 
                this.state.currentTime, 
                this.state.info.selectedSource.index,
                seconds,
            )
        } else {
            this.cast.playMovie(
                this.state.info.movie.id, 
                this.state.currentTime,
                this.state.info.selectedSource.index,
                this.state.info.audioLang,
                this.state.info.subtitleLang,
                seconds,
            )
        }
    }

    initCast() {
        this.cast.addEventListener(
            'anyChanged',
            this.castStateChanged.bind(this),
        )
    }

    playPauseClick(event) {
        this.cast.playOrPause()
    }

    castStateChanged(event) {
        switch (event.field) {
            case 'playerState':
                this.playerStateChanged(event)
                break
            case 'isConnected':
                this.connectedChanged()
                break
            case 'currentTime':
                this.currentTimeChanged(event)
                break
        }
    }

    connectedChanged() {
        const connected = this.cast.isConnected()
        this.setState({
            connected: connected,
            deviceName: (connected)?this.cast.getFriendlyName():'',
        })
        if (connected) {
            this.setState({loading: false})
            this.cast.getSession().addMessageListener(
                'urn:x-cast:net.seplis.cast.get_custom_data',
                this.receiveCastInfo.bind(this),
            )
        } else {
            this.setState({info: null})
        }
    }

    receiveCastInfo(namespace, message) {
        this.setState({
            info: JSON.parse(message),
            playNextEpisode: null,
            playerState: (this.cast.getMediaSession())?this.cast.getMediaSession().playerState:null,
        }, () => {
            if (this.cast.getMediaSession()) {
                this.currentTimeChanged({
                    value: this.cast.getMediaSession().getEstimatedTime()
                })
            }
            this.getPlayNextEpisode()
        })
    }

    playerStateChanged(event) {
        this.setState({
            playerState: event.value,
            loading: (event.value == 'BUFFERING') || this.changingTime,
        })
        if (!this.state.info)
            this.cast.getSession().sendMessage(
                'urn:x-cast:net.seplis.cast.get_custom_data', 
                {}
            )
        if (event.value == 'IDLE') {
            trigger_episode_watched_status('refresh', 0, 0)
        }
    }

    getPlayNextEpisode() {
        if (!this.state.info)
            return
        if (this.state.info.type != 'episode')
            return
        const number = parseInt(this.state.info.episode.number) + 1
        const showId = this.state.info.series.id
        request(
            `/1/shows/${showId}/episodes/${number}`
        ).done(data => {
            this.setState({nextEpisode: data})
        })
    }

    playNextEpisode() {
        if ((!this.state.nextEpisode) || (!this.state.info))
            return
        let info = this.state.info
        info['episode'] = this.state.nextEpisode
        info['startTime'] = 0
        this.setState({
            nextEpisode: null,
            info: info,
            playerState: '',
            loading: true,
            changingTime: true,
            currentTime: 0,
        })
        this.cast.playEpisode(
            this.state.info.series.id,
            this.state.nextEpisode.number,
            0,
        ).catch((e) => {
            alert(e.message)
            this.setState({changingTime: false})
        }).then(() => {
            this.setState({changingTime: false})
        }) 
    }

    currentTimeChanged(event) {
        let time = event.value
        const mediaSession = this.cast.getMediaSession()
        if (!mediaSession)
            return
        if (this.state.changingTime)
            return
        if (mediaSession.liveSeekableRange && this.state.info)
            time += this.state.info.startTime
        this.setState({currentTime: time})
    }

    sliderNewTime(newTime) {
        this.setState({
            loading: true,
            currentTime: newTime,
            changingTime: true,
            startTime: newTime,
        })
        this.cast.pause(() => {
            if (this.state.info.type == 'episode') {
                this.cast.playEpisode(
                    this.state.info.series.id,
                    this.state.info.episode.number,
                    newTime,
                    this.state.info.selectedSource.index,
                    this.state.info.subtitleOffset,
                ).catch((e) => {
                    this.setState({changingTime: false})
                    alert(e.message)
                }).then(() => {
                    this.setState({changingTime: false})
                })
            } else {
                this.cast.playMovie(
                    this.state.info.movie.id,
                    newTime,
                    this.state.info.selectedSource.index,
                    this.state.info.audioLang,
                    this.state.info.subtitleLang,
                    this.state.info.subtitleOffset,
                ).catch((e) => {
                    this.setState({changingTime: false})
                    alert(e.message)
                }).then(() => {
                    this.setState({changingTime: false})
                })
            }
        }, () => {            
            this.setState({changingTime: false})
        })
    }

    sliderReturnCurrentTime() {
        return this.state.currentTime
    }

    renderPlayControl() {
        if (this.state.loading) {
            return (
                <div className="control-icon">
                    <img src="/static/img/spinner.svg" />
                </div>
            )
        }
        let playPause = ClassNames({
            fa: true,
            'fa-pause': this.state.playerState == 'PLAYING',
            'fa-play': this.state.playerState != 'PLAYING',
        })
        return (
            <div className="control-icon">
                <i 
                    className={playPause}
                    onClick={this.onPlayPauseClick}
                >
                </i>
            </div>
        )
    }

    getDuration() {
        if (!this.state.info)
            return 0
        return parseInt(
            this.state.info.sources[0].duration
        )
    }

    getPlayNextInfo() {
        if (!this.state.info || !this.state.info.series || !this.state.nextEpisode) 
            return null
        const show = this.state.info.series
        const episode = this.state.nextEpisode
        const title = episodeTitle(show, episode)
        return {
            title: title,
            url: `/show/${show.id}/episode/${episode.number}/play`
        }
    }

    renderPlayNext() {
        if (!this.getPlayNextInfo()) 
            return
        return <div className="control-icon">
            <i 
                className="fas fa-step-forward"
                onClick={this.clickPlayNextEpisode}
            />
        </div>
    }

    renderTitle() {        
        if (this.state.info.type == 'movie') {
            return this.state.info.movie.title
        } else if (this.state.info.type == 'episode') {
            const show = this.state.info.series
            const episode = this.state.info.episode
            return `${show.title} - ${episodeTitle(show, episode)}`
        }
    }

    renderSettings() {
        if (!this.state.info)
            return
        return <div className="control-icon">
            <Settings 
                selectedSource={this.state.info.selectedSource}
                sources={this.state.info.sources}
                onAudioChange={this.onAudioChange}
                onSubtitleChange={this.onSubtitleChange}
                onResolutionChange={this.onResolutionChange}
                onSubtitleOffsetChange={this.onSubtitleOffsetChange}
                selectedSubtitleOffset={this.state.info.subtitleOffset}
            />
        </div>
    }

    renderPlaying() {
        return <div id="castbar">
            <div className="container">
                <div className="text">
                    <b>{this.renderTitle()}</b>
                    &nbsp; on {this.state.deviceName}
                </div>
                <div className="controls">
                </div>
                <div className="controls">
                    {this.renderPlayControl()}
                    <div className="control-text">
                        {secondsToTime(this.state.currentTime)}
                    </div>
                    <Slider
                        duration={this.getDuration()}
                        onReturnCurrentTime={this.onSliderReturnCurrentTime}
                        onNewTime={this.onSliderNewTime}
                    />
                    <div className="control-text">
                        {secondsToTime(this.getDuration())}
                    </div>
                    {this.renderPlayNext()}
                    {this.renderSettings()}
                </div>
            </div>
        </div>
    }

    renderFinished() {
        let show = this.state.info.series
        let episode = this.state.info.episode
        let playNext = this.getPlayNextInfo()
        if (!playNext) return null
        return (
            <div id="castbar">
            <div className="container">
                <div className="text">
                    <b>{this.state.deviceName}</b>
                    <br />
                    <b>Play next episode:</b> 
                    &nbsp; <a onClick={this.clickPlayNextEpisode}>
                        {show.title} - {playNext['title']}
                    </a>
                </div>
            </div>
            </div>
        )
    }

    renderLoading() {
        if (!this.state.loading)
            return
        return <img src="/static/img/spinner.svg" />
    }

    renderReadyToPlay() {
        return (
            <div id="castbar">
            <div className="container">
            <div className="text">
                <b>Ready to cast on {this.state.deviceName}</b> <br />
                {this.renderLoading()}
                {this.renderPlayNext()}
            </div>
            </div>
            </div>
        )
    }

    render() {
        if ((!this.cast) || (!this.state.connected)) {
            return null
        }
        if (this.state.info && (this.state.playerState == 'IDLE') && 
            !this.state.changingTime)
            return this.renderFinished()
        if (this.state.info)
            return this.renderPlaying()
        return this.renderReadyToPlay()
    }
}

export default ChromecastBar