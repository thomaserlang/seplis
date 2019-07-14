import React from 'react'
import ClassNames from 'classnames'
import Chromecast from './Chromecast'
import Slider from './Slider'
import AudioSubBar from './AudioSubBar.jsx'
import PlayNext from './PlayNext'
import {episodeTitle, secondsToTime} from 'utils'
import {request} from 'api'
import {trigger_episode_watched_status} from 'seplis/events'

import './ChromecastBar.scss'

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
        this.onAudioChange = this.audioChange.bind(this)
        this.onSubtitleChange = this.subtitleChange.bind(this)
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

        var session = this.cast.getSession()
        if (session) {
            session.removeMessageListener(
                'urn:x-cast:net.seplis.cast.get_custom_data',
                this.receiveCastInfo.bind(this),
            )
        }
    }

    audioChange(lang) {
        if (lang == '')
            lang = null
        this.subAudioSubSave({audio_lang: lang})
    }    

    subtitleChange(lang) {
        if (lang == '')
            lang = null
        this.subAudioSubSave({subtitle_lang: lang})
    }

    subAudioSubSave(data) {
        var show = this.state.info.show
        var episode = this.state.info.episode
        request(`/1/shows/${show.id}/user-subtitle-lang`, {
            method: 'PATCH',
            data: data,
        }).done(() => {
            this.cast.playEpisode(show.id, episode.number, this.state.currentTime)
        }).catch((e) => {
            alert(e.message)
        })
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
        let connected = this.cast.isConnected()
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
        let number = parseInt(this.state.info.episode.number) + 1
        let showId = this.state.info.show.id
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
            this.state.info.show.id,
            this.state.nextEpisode.number,
            0,
        ).catch((e) => {
            alert(e.message)
            this.setState({changingTime: false})
        }).then(() => {
            // iOS fix
            this.cast.getSession().sendMessage(
                'urn:x-cast:net.seplis.cast.get_custom_data', 
                {}
            )
            this.setState({changingTime: false})
        }) 
    }

    currentTimeChanged(event) {
        let time = event.value
        if (!this.cast.getMediaSession())
            return     
        if (!this.cast.getMediaSession().items)
            return
        if (this.cast.getMediaSession().items.length != 1)
            return
        if (this.state.changingTime)
            return
        let startTime = this.cast.getMediaSession().items[0].startTime
        if (startTime == 0 && this.state.info)
            time += this.state.info.startTime
        this.setState({currentTime: time})
    }

    sliderNewTime(newTime) {            
        this.state.info['startTime'] = newTime
        this.setState({
            loading: true,
            currentTime: newTime,
            changingTime: true,
        })
        this.cast.pause(() => {
            this.cast.playEpisode(
                this.state.info.show.id,
                this.state.info.episode.number,
                newTime,
            ).catch((e) => {
                this.setState({changingTime: false})
                alert(e.message)
            }).then(() => {
                // iOS fix
                this.cast.getSession().sendMessage(
                    'urn:x-cast:net.seplis.cast.get_custom_data', 
                    {}
                )
                this.setState({changingTime: false})
            })            
        })
    }

    sliderReturnCurrentTime() {
        return this.state.currentTime
    }

    renderPlayControl() {
        if (this.state.loading) {
            return (
                <div className="control">
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
            <div className="control">
                <span 
                    className={playPause}
                    onClick={this.onPlayPauseClick}
                >
                </span>
            </div>
        )
    }

    getDuration() {
        if (!this.state.info)
            return 0
        return parseInt(
            this.state.info.metadata.format.duration
        )
    }

    getPlayNextInfo() {
        if (!this.state.info || !this.state.info.show || !this.state.nextEpisode) 
            return null
        let show = this.state.info.show
        let episode = this.state.nextEpisode
        let title = episodeTitle(show, episode)
        return {
            title: title,
            url: `/show/${show.id}/episode/${episode.number}/play`
        }
    }

    renderPlayNext() {
        let info = this.getPlayNextInfo()
        if (!info) return
        return <div className="control">
            <span 
                className="fas fa-step-forward"
                onClick={this.clickPlayNextEpisode}
            />
        </div>
    }

    renderPlaying() {
        let show = this.state.info.show
        let episode = this.state.info.episode
        return (
            <div id="castbar">
            <div className="container">
                <div className="text">
                    <b>
                    {show.title} - {episodeTitle(show, episode)}
                    </b>
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
                    <div className="control">
                        <AudioSubBar 
                            metadata={this.state.info.metadata}
                            bottom={true}
                            onAudioChange={this.onAudioChange}
                            onSubtitleChange={this.onSubtitleChange}
                        />
                    </div>
                    {this.renderPlayNext()}
                </div>
            </div>
            </div>
        )
    }

    renderFinished() {
        let show = this.state.info.show
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