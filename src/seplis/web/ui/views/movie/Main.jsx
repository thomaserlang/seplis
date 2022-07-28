import React from 'react';
import WatchedButton from '../../components/movies/WatchedButton';
import Chromecast from 'seplis/components/player/Chromecast';

class Info extends React.Component {
    
    componentDidMount() {
        document.title = `${this.props.movie.title} | SEPLIS`
    }

    statusToText(status) {
        switch (status) {
            case 0: return 'Canceled';
            case 1: return 'Released';
            case 2: return 'Rumored';
            case 3: return 'Planned';
            case 4: return 'In production';
            case 5: return 'Post production';
            default: return 'Unknown';
        }
    }

    renderGeneral() {
        const movie = this.props.movie;
        return (
            <div className="col-12">
                <table className="table table-sm borderless">
                    <tbody>
                    <tr><th>Status</th><td>{this.statusToText(movie.status)}</td></tr>
                    <tr><th width="125">Release date</th><td>{movie.release_date || 'unknown'}</td></tr>
                    <tr><th>Runtime</th><td>{movie.runtime?movie.runtime + ' minutes':'Unknown'}</td></tr>
                    <tr><th>Language</th><td>{movie.language?movie.language:'Unknown'}</td></tr>
                    </tbody>
                </table>
            </div>
        )
    }

    renderDescription() {
        return (
            <div className="col-12 col-md-12">
                <p className="text-justify">
                    {this.props.movie.description}
                </p>
            </div>
        )
    }

    getPlayUrl() {
        return `/movie/${this.props.movie.id}/play`;
    }

    playClick = (e) => {
        if (Chromecast.session && (Chromecast.session.status == 'connected')) {
            let cc = new Chromecast();
            cc.playMovie(
                this.props.movie.id,
            ).catch((e) => {
                console.log(e)
                alert('Error occurred trying to play the movie on your Chrome Cast')
            });
        } else {
            location.href = this.getPlayUrl();
        }
    }

    renderWatched() {
        return <div className="col-12 col-md-12 mt-4"> 
            <div className="button-bar d-flex">
                <WatchedButton movieId={this.props.movie.id} />
                <div 
                    className="play-button ml-3"
                    onClick={this.playClick}
                >
                    <i className="fas fa-play-circle"></i>
                </div>
            </div>
        </div>
    }

    render() {
        return (
            <div className="row">
                {this.renderGeneral()}                
                {this.renderDescription()}
                {this.renderWatched()}
            </div>
        )
    }
}

export default Info;