import React from 'react';
import ClassNames from 'classnames';
import {request} from 'api';
import PlayNext from './PlayNext';
import VolumeBar from './VolumeBar';
import AudioSubBar from './AudioSubBar.jsx';
import Slider from './Slider.jsx';
import ChromecastIcon from './ChromecastIcon';
import Loader from 'seplis/components/Loader';
import {secondsToTime} from 'utils';
import './Player.scss';

const propTypes = {
    playServerUrl: React.PropTypes.string,
    playId: React.PropTypes.string,
    session: React.PropTypes.string,
    startTime: React.PropTypes.number,
    metadata: React.PropTypes.object,
    info: React.PropTypes.object,
    nextInfo: React.PropTypes.object,
    backToInfo: React.PropTypes.object,
    currentInfo: React.PropTypes.object,
    onAudioChange: React.PropTypes.func,
    onSubtitleChange: React.PropTypes.func,
    audio_lang: React.PropTypes.string,
    subtitle_lang: React.PropTypes.string,
    onTimeUpdate: React.PropTypes.func,
}

const defaultProps = {
    startTime: 0,
    info: null,
    nextInfo: null,
}

class Player extends React.Component {

    constructor(props) {
        super(props);
        this.onPlayPauseClick = this.playPauseClick.bind(this);
        this.duration = parseInt(props.metadata.format.duration);
        this.pingTimer = null;
        this.onFullscreenClick = this.fullscreenClick.bind(this);
        this.onVolumeChange = this.volumeChange.bind(this);

        this.onAudioChange = this.audioChange.bind(this);
        this.onSubtitleChange = this.subtitleChange.bind(this);

        this.volume = 1;
        this.hideControlsTimer = null;

        this.onSliderReturnCurrentTime = this.sliderReturnCurrentTime.bind(this);
        this.onSliderNewTime = this.sliderNewTime.bind(this);

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
        this.video.addEventListener('timeupdate', this.timeupdateEvent.bind(this));
        this.video.addEventListener('pause', this.pauseEvent.bind(this));
        this.video.addEventListener('play', this.playEvent.bind(this));
        this.video.addEventListener('fullscreenchange', this.fullscreenchangeEvent.bind(this));
        this.video.addEventListener('error', this.playError.bind(this));
        this.video.addEventListener('waiting', this.playWaiting.bind(this));
        this.setPingTimer();
        this.video.volume = this.volume;
        this.video.load();
        document.onmousemove = this.mouseMove.bind(this);
        document.ontouchstart = document.onmousemove;
        document.ontouchmove = this.touchMove.bind(this);
        document.onclick = this.click.bind(this);
        document.onkeypress = this.keypress.bind(this);
    }

    keypress(e) {
        if (e.code == 'Space')
            this.playPauseClick();
    }

    click(e) {
        this.setState({showControls: !this.state.showControls});
        this.setHideControlsTimer();
    }

    setPingTimer() {
        this.pingTimer = setTimeout(() => {
            request(this.getPlayUrl()+'&action=ping');
            this.setPingTimer();
        }, 30000);
    }

    setHideControlsTimer(timeout) {
        if (timeout == undefined)
            timeout = 6000;
        clearTimeout(this.hideControlsTimer);
        this.hideControlsTimer = setTimeout(() => {
            if (this.video.paused || this.state.loading)
                return;
            this.setState({
                showControls: false,
            });
        }, timeout);
    }

    mouseMove(e) {
        if (this.state.showControls) return;
        this.setState({
            showControls: true,
        });
        this.setHideControlsTimer();
    }

    touchMove(e) {
        // disable scroll bounce effect on iOS
        e.preventDefault();
    }

    getPlayUrl() {
        return `${this.props.playServerUrl}/play`+
            `?play_id=${this.props.playId}`+
            `&session=${this.props.session}`+
            `&start_time=${this.state.startTime}`+
            `&subtitle_lang=${this.state.subtitle || ''}`+
            `&audio_lang=${this.state.audio || ''}`
    }

    playPauseClick() {
        if (this.video.paused) {
            this.video.play();
            this.setHideControlsTimer(2000);
        }
        else
            this.video.pause();
    }

    fullscreenchangeEvent() {
        this.setState({
            fullscreen: document.fullScreen,
        });
    }

    pauseEvent() {
        this.setState({
            playing: false,
            showControls: true,
        });
    }

    playEvent() {
        this.setState({
            playing: true,
            loading: true,
        });
    }

    playError() {
        this.setState({loading: false});
    }

    playWaiting() {
        this.setState({loading: true});
    }

    timeupdateEvent(e) {
        this.setState({loading: false});
        if (!this.video.paused) {
            let time = this.video.currentTime;
            if (this.video.seekable.length <= 1 || this.video.seekable.end(0) <= 1)
                time += this.state.startTime;
            this.setState({
                time: time,
                playing: true,
            }, () => {
                if (this.props.onTimeUpdate)
                    this.props.onTimeUpdate(this.state.time);
            });
            if (!this.hideControlsTimer) {
                this.setHideControlsTimer();
            }
        }
    }

    changeVideoState(state) {
        request(
            this.getPlayUrl()+'&action=cancel'
        ).success(() => {
            this.setState(state, () => {
                this.video.load();
                this.video.play();
            });
        });
    }

    fullscreenClick(event) {
        if (!this.state.fullscreen) {
            if (this.video.requestFullScreen) {
                this.video.requestFullScreen();
            } else if (this.video.mozRequestFullScreen) {
                this.video.mozRequestFullScreen();
            } else if (this.video.webkitRequestFullScreen) {
                this.video.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
            } else if (this.video.webkitEnterFullscreen) {
                this.video.webkitEnterFullscreen();
            }
        } else {
            if (document.cancelFullScreen) {
                document.cancelFullScreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.webkitCancelFullScreen) {
                document.webkitCancelFullScreen();
            }
        }
        this.setState({fullscreen: !this.state.fullscreen});
    }

    getDurationText() {
        return secondsToTime(parseInt(this.duration));
    }

    getCurrentTimeText() {
        return secondsToTime(parseInt(this.state.time));
    }

    renderPlayNext() {
        if (!this.props.nextInfo) return;
        return (
            <PlayNext
                title={this.props.nextInfo.title}
                url={this.props.nextInfo.url}
            />    
        )
    }

    volumeChange(volume) {
        this.volume = volume;
        if (this.video)
            this.video.volume = volume;
    }

    audioChange(lang) {
        if (this.props.onAudioChange)
            this.props.onAudioChange(lang);
        this.changeVideoState({
            audio: lang,
            startTime: this.state.time,
        });
    }

    subtitleChange(lang) {
        if (this.props.onSubtitleChange)
            this.props.onSubtitleChange(lang);
        this.changeVideoState({
            subtitle: lang,
            startTime: this.state.time,
        });
    }

    sliderNewTime(newTime) {
        this.video.pause();        
        clearTimeout(this.hideControlsTimer);
        this.hideControlsTimer = null;
        this.changeVideoState({
            time: newTime,
            startTime: newTime,
        });
    }

    sliderReturnCurrentTime() {
        return this.state.time;
    }

    showControlsVisibility() {
        return this.state.showControls?'visible':'hidden';
    }

    renderControlsTop() {
        return (
            <div 
                className="controls controls-top" 
                style={{visibility: this.showControlsVisibility()}}
            >
                <div className="control">
                    <a 
                        className="fa fa-times" 
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
        });
        let fullscreen = ClassNames({
            fa: true,
            'fa-expand': this.state.fullscreen,
            'fa-arrows-alt': !this.state.fullscreen,
        });
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
            return null;
        return <Loader hcenter={true} />
    }

    render() {
        return (
            <div className="player">  
                <div className="overlay">
                    <video 
                        className="video" 
                        preload="none" 
                        autoPlay={true}
                        src={this.getPlayUrl()}
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
Player.propTypes = propTypes;
Player.defaultProps = defaultProps;
export default Player;

export function getPlayServer(url) {
    /* `url` must be a url to the play servers. 
        Example: /1/shows/1/episodes/1/play-servers.

        Returns a promise.
    */
    return new Promise((resolve, reject) => {
        request(
            url
        ).success(playServers => {
            var selected = false;
            var i = 0;
            if (playServers.length == 0) {
                reject({code: 1, message: 'No play servers.'});
                return;
            }
            for (var s of playServers) {
                i += 1;
                request(s.play_server.url+'/metadata', {
                    query: {
                        play_id: s.play_id,
                    }
                }).success(metadata => {
                    if (selected) 
                        return;
                    selected = true;
                    resolve({
                        playServer: s, 
                        metadata: metadata,
                    });
                }).always(() => {
                    i -= 1;
                    if ((i == 0) && (selected == false)) {
                        reject({code: 2, message: 'The episode is not on any of your play servers.'});
                    }
                });
            }
        });
    });
}