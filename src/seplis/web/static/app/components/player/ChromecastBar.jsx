import React from 'react';
import ClassNames from 'classnames';
import Chromecast from './Chromecast';
import Slider from './Slider';
import AudioSubBar from './AudioSubBar.jsx';
import {episodeTitle, getUserId, secondsToTime} from 'utils';
import {request} from 'api';

import './ChromecastBar.scss';

class ChromecastBar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            connected: false,
            deviceName: "",
            playing: false,
            info: null,
            currentTime: 0,
            loading: false,
        }
        this.cast = null;

        this.onSliderReturnCurrentTime = this.sliderReturnCurrentTime.bind(this);
        this.onSliderNewTime = this.sliderNewTime.bind(this);
        this.onPlayPauseClick = this.playPauseClick.bind(this);
        this.onAudioChange = this.audioChange.bind(this);
        this.onSubtitleChange = this.subtitleChange.bind(this);
    }

    componentDidMount() {
        this.cast = new Chromecast();
        this.cast.load(this.initCast.bind(this));
    }

    componentWillUnmount() {
        this.cast.removeEventListener(
            'anyChanged',
            this.castStateChanged.bind(this)
        );

        var session = this.cast.getSession();
        if (session) {
            session.removeMessageListener(
                'urn:x-cast:net.seplis.cast.info',
                this.receiveCastInfo.bind(this),
            );
        }
    }

    audioChange(lang) {
        if (lang == '')
            lang = null;
        this.subAudioSubSave({audio_lang: lang});
    }    

    subtitleChange(lang) {
        if (lang == '')
            lang = null;
        this.subAudioSubSave({subtitle_lang: lang});
    }

    subAudioSubSave(data) {
        var show = this.state.info.show;
        var episode = this.state.info.episode;
        request(`/1/users/${getUserId()}/subtitle-lang/shows/${show.id}`, {
            method: 'PATCH',
            data: data,
        }).success(() => {
            this.cast.playEpisode(show.id, episode.number, this.state.currentTime);
        });
    }

    initCast() {
        this.cast.addEventListener(
            'anyChanged',
            this.castStateChanged.bind(this),
        )
    }

    playPauseClick(event) {
        this.cast.playOrPause();
    }

    castStateChanged(event) {
        switch (event.field) {
            case 'playerState':
                this.playerStateChanged(event);
                break;
            case 'isConnected':
                this.connectedChanged();
                break;
            case 'currentTime':
                this.currentTimeChanged(event);
                break;
        }
    }

    connectedChanged() {
        let connected = this.cast.isConnected();
        this.setState({
            connected: connected,
            deviceName: (connected)?this.cast.getFriendlyName():'',
        });
        if (connected) {
            this.setState({loading: false});
            this.cast.getSession().addMessageListener(
                'urn:x-cast:net.seplis.cast.info',
                this.receiveCastInfo.bind(this),
            );
            this.cast.getSession().sendMessage(
                'urn:x-cast:net.seplis.cast.sendinfo', 
                {}
            );
        } else {
            this.setState({info: null});
        }
    }

    receiveCastInfo(namespace, message) {
        this.setState({
            info: JSON.parse(message),
        }, () => {
            if (this.cast.getMediaSession()) {
                this.currentTimeChanged({
                    value: this.cast.getMediaSession().getEstimatedTime()
                });
            }
        });
    }

    playerStateChanged(event) {
        this.setState({
            playing: (event.value == 'PLAYING'),
            loading: (event.value == 'BUFFERING' || event.value == 'IDLE'),
        });
        if (event.value == 'IDLE')
            this.setState({info: null, loading: false});
        if (event.value == 'BUFFERING' || event.value == 'PLAYING') {
            if (!this.state.info)
                this.cast.getSession().sendMessage(
                    'urn:x-cast:net.seplis.cast.sendinfo', 
                    {}
                );   
        }
    }

    currentTimeChanged(event) {
        let time = event.value;
        if (!this.cast.getMediaSession())
            return;     
        if (!this.cast.getMediaSession().items)
            return;
        if (this.cast.getMediaSession().items.length != 1)
            return;
        let startTime = this.cast.getMediaSession().items[0].startTime;
        if (startTime == 0 && this.state.info)
            time += this.state.info.startTime;
        this.setState({currentTime: time});
    }

    sliderNewTime(newTime) {
        this.cast.pause(() => {
            this.setState({
                loading: true,
                currentTime: newTime,
            });
            this.cast.playEpisode(
                this.state.info.show.id,
                this.state.info.episode.number,
                newTime,
            );            
        });
    }

    sliderReturnCurrentTime() {
        return this.state.currentTime;
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
            'fa-pause': this.state.playing,
            'fa-play': !this.state.playing,
        });
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
            return 0;
        return parseInt(
            this.state.info.metadata.format.duration
        );
    }

    renderPlaying() {
        let show = this.state.info.show;
        let episode = this.state.info.episode;
        return (
            <div id="castbar">
            <div className="container">
                <div className="text">
                    <b>Playing on {this.state.deviceName}:</b> 
                    &nbsp; {show.title} - {episodeTitle(show, episode)}
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
                </div>
            </div>
            </div>
        )
    }

    renderLoading() {
        if (!this.state.loading)
            return;
        return <img src="/static/img/spinner.svg" />;
    }

    renderReadyToPlay() {
        return (
            <div id="castbar">
            <div className="container">
            <div className="text">
                <b>Ready to cast on {this.state.deviceName}</b> <br />
                {this.renderLoading()}
            </div>
            </div>
            </div>
        )
    }

    render() {
        if ((!this.cast) || (!this.state.connected)) {
            return null;
        }
        if (this.state.info)
            return this.renderPlaying();
        return this.renderReadyToPlay();
    }
}

export default ChromecastBar;