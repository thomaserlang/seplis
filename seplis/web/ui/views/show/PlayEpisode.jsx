import React from 'react'
import Player, {getPlayServer} from 'seplis/components/player/Player'
import Loader from 'seplis/components/Loader'
import Chromecast from 'seplis/components/player/Chromecast'
import {request} from 'seplis/api'
import {episodeTitle, guid, dateInDays} from 'seplis/utils'
 
class PlayEpisode extends React.Component {
 
    constructor(props) {
        super(props)
        this.state = {
            loadingPlayServers: true,
            loadingShow: true,
            loadingEpisode: true,
            loadingNextEpisode: true,
            loadingLang: true,
            loadingStartTime: true,
            playServer: null,
            playServerError: null,
            show: null,
            episode: null,
            nextEpisode: null,
            audio_lang: null,
            subtitle_lang: null,
            sources: null,
            startTime: 0,
        }        
        this.onAudioChange = this.audioChange.bind(this)
        this.onSubtitleChange = this.subtitleChange.bind(this)
        this.onTimeUpdate = this.timeUpdate.bind(this)
        this.showId = this.props.match.params.showId
        this.number = this.props.match.params.number
        this.lastPos = 0
        this.cast = null
        this.markedAsWatched = false
    }
 
    componentDidMount() {
        this.getShow()
        this.getEpisode()
        this.getPlayServers()
        this.getNextEpisode()
        this.getLanguage()
        this.getStartTime()
    }
 
    timeUpdate(time, duration) {
        time = Math.floor(time)
        if (this.state.startTime == time)
            return
        if (time == this.lastPos) 
            return
        this.lastPos = time
        if (time < 10)
            return
        if ((time % 10) != 0) 
            return
        let watched = (((time / 100) * 10) > (duration-time))
        if (watched) {
            if (!this.markedAsWatched) {
                request(`/1/shows/${this.showId}/episodes/${this.number}/watched`, {
                    method: 'PUT',
                }).done(() => {
                    this.markedAsWatched = true
                })
            }
        } else {
            this.markedAsWatched = false
            request(`/1/shows/${this.showId}/episodes/${this.number}/position`, {
                method: 'PUT',
                data: {
                    'position': time,
                }
            })
        }
    }
 
    getPlayServers() {
        let url = `/1/shows/${this.showId}/episodes/${this.number}/play-servers`
        getPlayServer(url).then((obj) => {
            this.setState({
                loadingPlayServers: false,
                playServer: obj.playServer,
                sources: obj.sources,
            })
        }).catch((error) => {
            this.setState({
                loadingPlayServers: false,
                playServerError: error,
            })
        })
    }
 
    getShow() {
        request(
            `/1/shows/${this.showId}`
        ).done(data => {
            this.setState({show: data})
        }).always(() => {
            this.setState({loadingShow: false})
        })        
    }
 
    getEpisode() {
        let number = parseInt(this.number)
        request(
            `/1/shows/${this.showId}/episodes/${number}`
        ).done(data => {
            this.setState({episode: data})
        }).always(() => {
            this.setState({loadingEpisode: false})
        })
    }    
 
    getNextEpisode() {
        let number = parseInt(this.number) + 1
        request(
            `/1/shows/${this.showId}/episodes/${number}`
        ).done(data => {
            this.setState({nextEpisode: data})
        }).always(() => {
            this.setState({loadingNextEpisode: false})
        })
    }
 
    getLanguage() {
        request(
            `/1/shows/${this.showId}/user-subtitle-lang`
        ).done(data => {
            if (!data)
                data = {}
            this.setState({
                audio_lang: data.audio_lang || null,
                subtitle_lang: data.subtitle_lang || null,
            })
        }).always(() => {
            this.setState({loadingLang: false})
        })
    }
 
    getStartTime() {
        request(
            `/1/shows/${this.showId}/episodes/${this.number}/watched`
        ).done(data => {
            if (data) {
                this.setState({
                    startTime: data.position,
                })
            } else {
                this.setState({
                    startTime: 0,
                })                
            }
        }).always(() => {
            this.setState({loadingStartTime: false})
        })
    }
 
    audioChange(lang) {
        if (lang == '') 
            lang = null
        this.saveSub({
            audio_lang: lang,
        })
    } 
 
    subtitleChange(lang) {
        if (lang == '') 
            lang = null
        this.saveSub({
            subtitle_lang: lang,
        })
    }
 
    saveSub(data) {
        request(`/1/shows/${this.showId}/user-subtitle-lang`, {
            method: 'PATCH',
            data: data,
        })
    }
 
    getInfo() {
        if (!this.state.show) return null
        return {
            title: this.state.show.title,
        }
    }
 
    episodeTitle(show, episode) {
        return episodeTitle(show, episode)
    }
 
    getPlayNextInfo() {
        if (!this.state.show || !this.state.nextEpisode) return null
        let show = this.state.show
        let episode = this.state.nextEpisode
        let title = this.episodeTitle(show, episode)
        return {
            title: title,
            url: `/show/${show.id}/episode/${episode.number}/play`
        }
    }
 
    getBackToInfo() {
        if (!this.state.show) return null
        return {
            title: `Back to: ${this.state.show.title}`,
            url: `/show/${this.showId}`
        }
    }
 
    getCurrentInfo() {
        if (!this.state.show || !this.state.episode) return null
        let show = this.state.show
        let title = `${show.title} - `
        title += this.episodeTitle(show, this.state.episode)
        return {
            title: title,
        }
    }
  
    initCast() {
        this.cast.addEventListener(
            'isConnected',
            (e) => {
                if (!e.value) 
                    return
                if (!confirm(`Play ${this.getCurrentInfo().title} on ${this.cast.getFriendlyName()}?`))
                    return
                this.cast.playEpisode(this.showId, this.number).then(() => {
                    location.href = `/show/${this.showId}`
                })
            },
        )
    }
 
    loadCast() {
        if (this.cast)
            return    
        this.cast = new Chromecast()
        this.cast.load(this.initCast.bind(this))
    }

    renderPlayServerErrorMessage() {
        if (this.state.playServerError.code == 2) {
            return <span>
                    <h3>
                        "{this.state.show.title} {episodeTitle(this.state.show, this.state.episode)}" is not on any of your play servers.
                    </h3>
                    {this.renderAirs()}
            </span>
        }
        return this.state.playServerError.message
    }

    renderAirs() {
        if (!this.state.episode.air_datetime)
            return
        let d = new Date(this.state.episode.air_datetime)
        let now = new Date()
        if ((now.getTime()-d.getTime()) > 3600*24)
            return
        if (now.getTime() < d.getTime()) {
            return <div className="mb-2">
                Airs in {dateInDays(this.state.episode.air_datetime)}
            </div>
        } else {
            return <div>
                Aired {dateInDays(this.state.episode.air_datetime)} ago
            </div>
        }
    }

    renderPlayServerError() {
        return (
            <div 
                className="alert alert-warning" 
                style={{width: '75%', margin: 'auto', marginTop: '100px'}}
            >
                {this.renderPlayServerErrorMessage()}

                Go back to <a href={`/show/${this.showId}`}>
                    {this.state.show.title}
                </a>
            </div>
        )
    }

    render() {
        if (this.state.loadingPlayServers || this.state.loadingShow ||
            this.state.loadingEpisode || this.state.loadingNextEpisode ||
            this.state.loadingLang || this.state.loadingStartTime)
            return <Loader />
        if (this.state.playServerError) {
            return this.renderPlayServerError()
        }
        this.loadCast()
        return <Player 
            playServerUrl={`${this.state.playServer.play_url}`}
            playId={this.state.playServer.play_id}
            sources={this.state.sources}
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
        />
    }
}
export default PlayEpisode