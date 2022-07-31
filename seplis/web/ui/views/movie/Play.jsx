import React from 'react'
import Player, {getPlayServer} from 'seplis/components/player/Player'
import Loader from 'seplis/components/Loader'
import Chromecast from 'seplis/components/player/Chromecast'
import {request} from 'seplis/api'
import { guid } from 'seplis/utils'
 
class Play extends React.Component {
 
    constructor(props) {
        super(props)
        this.state = {
            loadingPlayServers: true,
            loadingMovie: true,
            loadingStartTime: true,
            playServer: null,
            playServerError: null,
            movie: null,
            metadata: null,
            startTime: 0,
        }        
        this.onAudioChange = this.audioChange.bind(this)
        this.onSubtitleChange = this.subtitleChange.bind(this)
        this.onTimeUpdate = this.timeUpdate.bind(this)
        this.movieId = this.props.match.params.movieId
        this.number = this.props.match.params.number
        this.session = guid()
        this.lastPos = 0
        this.cast = null
        this.markedAsWatched = false
    }
 
    componentDidMount() {
        this.getMovie()
        this.getPlayServers()
        this.getLanguage()
        this.getStartTime()
    }
 
    timeUpdate(time) {
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
        let duration = parseInt(this.state.metadata['format']['duration'])
        let watched = (((time / 100) * 10) > (duration-time))
        if (watched) {
            if (!this.markedAsWatched) {
                request(`/1/movies/${this.movieId}/watched`, {
                    method: 'POST',
                }).done(() => {
                    this.markedAsWatched = true
                })
            }
        } else {
            this.markedAsWatched = false
            request(`/1/movies/${this.movieId}/position`, {
                method: 'PUT',
                data: {
                    'position': time,
                }
            })
        }
    }
 
    getPlayServers() {
        let url = `/1/movies/${this.movieId}/play-servers`
        getPlayServer(url).then((obj) => {
            this.setState({
                loadingPlayServers: false,
                playServer: obj.playServer,
                metadata: obj.metadata[0],
            })
        }).catch((error) => {
            this.setState({
                loadingPlayServers: false,
                playServerError: error,
            })
        })
    }
 
    getMovie() {
        request(
            `/1/movies/${this.movieId}`
        ).done(data => {
            this.setState({movie: data})
        }).always(() => {
            this.setState({loadingMovie: false})
        })        
    }
 
    getLanguage() {
    }
 
    getStartTime() {
        request(
            `/1/movies/${this.movieId}/watched`
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
    } 
 
    subtitleChange(lang) {
        if (lang == '') 
            lang = null
    }
 
    saveSub(data) {
    }
 
    getInfo() {
        if (!this.state.movie) return null
        return {
            title: this.state.movie.title,
        }
    }
  
    getBackToInfo() {
        if (!this.state.movie) return null
        return {
            title: `Back to: ${this.state.movie.title}`,
            url: `/movie/${this.movieId}`
        }
    }
 
    getCurrentInfo() {
        if (!this.state.movie) return null
        return {
            title: this.state.movie.title,
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
                request(`${this.state.playServer.play_url}/close-session/${this.session}`)
                this.cast.playMovie(this.movieId).then(() => {
                    location.href = `/movie/${this.movieId}`
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
 
    getPlayUrl() {
        return `${this.state.playServer.play_url}/play`+
            `?play_id=${this.state.playServer.play_id}`+
            `&session=${this.session}`
    }

    renderPlayServerErrorMessage() {
        if (this.state.playServerError.code == 2) {
            return <span>
                <h3>
                    "{this.state.movie.title}" is not on any of your play servers.
                </h3>
                <div>Release date: {this.state.movie.release_date}</div>
            </span>
        }
        return this.state.playServerError.message
    }

    renderPlayServerError() {
        return (
            <div 
                className="alert alert-warning" 
                style={{width: '75%', margin: 'auto', marginTop: '100px'}}
            >
                {this.renderPlayServerErrorMessage()}

                Go back to <a href={`/movie/${this.movieId}`}>
                    {this.state.movie.title}
                </a>
            </div>
        )
    }

    render() {
        if (this.state.loadingPlayServers || this.state.loadingMovie ||
            this.state.loadingStartTime)
            return <Loader />
        if (this.state.playServerError) {
            return this.renderPlayServerError()
        }
        this.loadCast()
        return <Player 
            playServerUrl={`${this.state.playServer.play_url}`}
            playId={this.state.playServer.play_id}
            metadata={this.state.metadata}
            info={this.getInfo()}
            //nextInfo={this.getPlayNextInfo()}
            backToInfo={this.getBackToInfo()}
            currentInfo={this.getCurrentInfo()}
            onAudioChange={this.onAudioChange}
            onSubtitleChange={this.onSubtitleChange}
            //audio_lang={this.state.audio_lang}
            subtitle_lang={this.state.subtitle_lang}
            onTimeUpdate={this.onTimeUpdate}
            startTime={this.state.startTime}
            session={this.session}
        />
    }
}
export default Play