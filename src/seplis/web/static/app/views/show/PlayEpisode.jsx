import React from 'react';
import Player, {getPlayServer} from 'components/player/Player';
import Loader from 'components/Loader';
import ChromecastLoad from 'components/player/ChromecastLoad';
import {request} from 'api';
import {apiClientSettings} from 'api.jsx';
import {pad, getUserId, episodeTitle, guid} from 'utils';
 
class PlayEpisode extends React.Component {
 
    constructor(props) {
        super(props);
        this.state = {
            loadingPlayServers: true,
            loadingShow: true,
            loadingEpisode: true,
            loadingNextEpisode: true,
            loadingLang: true,
            loadingStartTime: true,
            playServer: null,
            show: null,
            episode: null,
            nextEpisode: null,
            audio_lang: null,
            subtitle_lang: null,
            metadata: null,
            startTime: 0,
        }        
        this.onAudioChange = this.audioChange.bind(this);
        this.onSubtitleChange = this.subtitleChange.bind(this);
        this.onTimeUpdate = this.timeUpdate.bind(this);
 
        this.showId = this.props.params.showId;
        this.number = this.props.params.number;
        this.session = guid();
        this.lastPos = 0;
        this.cast = null;
    }
 
    componentDidMount() {
        this.getShow();
        this.getEpisode();
        this.getPlayServers();
        this.getNextEpisode();
        this.getLanguage();
        this.getStartTime();
    }
 
    timeUpdate(time) {
        time = Math.floor(time);
        if (time == this.lastPos) 
            return;
        this.lastPos = time;
        if ((time % 10) != 0) 
            return;
        let duration = parseInt(this.state.metadata['format']['duration']);
        let watched = (((time / 100) * 10) > (duration-time));
        if (watched) {
            request(`/1/shows/${this.showId}/episodes/${this.number}/watched`, {
                method: 'PUT',
            });
        } else {
            request(`/1/shows/${this.showId}/episodes/${this.number}/watching`, {
                method: 'PUT',
                data: {
                    'position': time,
                }
            });
        }
    }
 
    getPlayServers() {
        let url = `/1/shows/${this.showId}/episodes/${this.number}/play-servers`;
        getPlayServer(url).then((obj) => {
            this.setState({
                loadingPlayServers: false,
                playServer: obj.playServer,
                metadata: obj.metadata,
            });
        });
    }
 
    getShow() {
        request(
            `/1/shows/${this.showId}`
        ).success(data => {
            this.setState({show: data});
        }).always(() => {
            this.setState({loadingShow: false});
        });        
    }
 
    getEpisode() {
        let number = parseInt(this.number);
        request(
            `/1/shows/${this.showId}/episodes/${number}`
        ).success(data => {
            this.setState({episode: data});
        }).always(() => {
            this.setState({loadingEpisode: false});
        });
    }    
 
    getNextEpisode() {
        let number = parseInt(this.number) + 1;
        request(
            `/1/shows/${this.showId}/episodes/${number}`
        ).success(data => {
            this.setState({nextEpisode: data});
        }).always(() => {
            this.setState({loadingNextEpisode: false});
        });
    }
 
    getLanguage() {
        request(
            `/1/users/${getUserId()}/subtitle-lang/shows/${this.showId}`
        ).success(data => {
            if (!data)
                data = {};
            this.setState({
                audio_lang: data.audio_lang || null,
                subtitle_lang: data.subtitle_lang || null,
            });
        }).always(() => {
            this.setState({loadingLang: false});
        });
    }
 
    getStartTime() {
        request(
            `/1/shows/${this.showId}/episodes/${this.number}/watched`
        ).success(data => {
            if (data) {
                this.setState({
                    startTime: data.position,
                });
            } else {
                this.setState({
                    startTime: 0,
                });                
            }
        }).always(() => {
            this.setState({loadingStartTime: false});
        });
    }
 
    audioChange(lang) {
        if (lang == '') 
            lang = null;
        this.saveSub({
            audio_lang: lang,
        });
    } 
 
    subtitleChange(lang) {
        if (lang == '') 
            lang = null;
        this.saveSub({
            subtitle_lang: lang,
        });
    }
 
    saveSub(data) {
        request(`/1/users/${getUserId()}/subtitle-lang/shows/${this.showId}`, {
            method: 'PATCH',
            data: data,
        })
    }
 
    getInfo() {
        if (!this.state.show) return null;
        return {
            title: this.state.show.title,
        }
    }
 
    episodeTitle(show, episode) {
        return episodeTitle(show, episode);
    }
 
    getPlayNextInfo() {
        if (!this.state.show || !this.state.nextEpisode) return null;
        let show = this.state.show;
        let episode = this.state.nextEpisode;
        let title = this.episodeTitle(show, episode);
        return {
            title: title,
            url: `/show/${show.id}/episode/${episode.number}/play`
        }
    }
 
    getBackToInfo() {
        if (!this.state.show) return null;
        return {
            title: `Back to: ${this.state.show.title}`,
            url: `/show/${this.showId}`
        }
    }
 
    getCurrentInfo() {
        if (!this.state.show || !this.state.episode) return null;
        let show = this.state.show;
        let title = `${show.title} - `;
        title += this.episodeTitle(show, this.state.episode);
        return {
            title: title,
        }
    }
  
    initCast() {
        this.cast.addEventListener(
            'isConnected',
            (e) => {
                if (!e.value) 
                    return;
                if (!confirm(`Play ${this.getCurrentInfo().title} on ${this.cast.getFriendlyName()}?`))
                    return;
                request(this.getPlayUrl()+'&action=cancel');
                this.cast.playEpisode(this.showId, this.number).then(() => {
                    location.href = `/show/${this.showId}`;
                });
            },
        );
    }
 
    loadCast() {
        if (this.cast)
            return;    
        this.cast = new ChromecastLoad(this.initCast.bind(this));
    }    
 
    getPlayUrl() {
        return `${this.state.playServer.play_server.url}/play2`+
            `?play_id=${this.state.playServer.play_id}`+
            `&session=${this.session}`
    }
 
    render() {
        if (this.state.loadingPlayServers || this.state.loadingShow ||
            this.state.loadingEpisode || this.state.loadingNextEpisode ||
            this.state.loadingLang || this.state.loadingStartTime)
            return <Loader />;
        this.loadCast();
        return <Player 
            playServerUrl={`${this.state.playServer.play_server.url}`}
            playId={this.state.playServer.play_id}
            metadata={this.state.metadata}
            info={this.getInfo()}
            nextInfo={this.getPlayNextInfo()}
            backToInfo={this.getBackToInfo()}
            currentInfo={this.getCurrentInfo()}
            onAudioChange={this.onAudioChange}
            onSubtitleChange={this.onSubtitleChange}
            audio_lang={this.state.audio_lang}
            subtitle_lang={this.state.subtitle_lang}
            onTimeUpdate={this.onTimeUpdate}
            startTime={this.state.startTime}
            session={this.session}
        />;
    }
}
export default PlayEpisode;