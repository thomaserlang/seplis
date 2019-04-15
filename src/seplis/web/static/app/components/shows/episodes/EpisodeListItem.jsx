import React from 'react';
import PropTypes from 'prop-types';
import WatchedButton from './WatchedButton';
import Chromecast from 'seplis/components/player/Chromecast';

import './EpisodeListItem.scss';

const propTypes = {
    showId: PropTypes.number.isRequired,
    episode: PropTypes.object.isRequired,
    displaySeason: PropTypes.bool,
}

const defaultProps = {
    displaySeason: true,
}

class EpisodeListItem extends React.Component {

    constructor(props) {
        super(props);
        this.onPlayClick = this.playClick.bind(this);
    }

    playClick(e) {
        if (Chromecast.session && (Chromecast.session.status == 'connected')) {
            let cc = new Chromecast();
            cc.playEpisode(
                this.props.showId,
                this.props.episode.number
            ).catch((e) => {
                alert(e.message)
            });
        } else {
            location.href = this.getPlayUrl();
        }
    }

    renderEpisodeNumber() {
        if (this.props.episode.episode) {
            return (
                <span>
                    {this.props.displaySeason?`S${this.props.episode.season} `: ''}
                    Episode {this.props.episode.episode}
                    &nbsp;
                    <font color="grey">
                        ({this.props.episode.number})
                    </font> 
                </span>
            )
        } else {
            return (
                <span>Episode {this.props.episode.number}</span>
            )   
        }
    }

    renderAirDate() {
        if (this.props.episode.air_date) {
            return (
                <span 
                    className="air-date" 
                    title={this.props.episode.air_date}
                >
                    {this.props.episode.air_date}
                </span> 
            )
        } else {
            return (
                <span>
                    Unknown air date.
                </span>
            )
        }
    }

    getPlayUrl() {
        return `/show/${this.props.showId}/episode/${this.props.episode.number}/play`;
    }

    render() {
        return (
            <div className="episode-box-list-item">
                <div 
                    className="title" 
                    title={this.props.episode.title}
                >
                    {this.props.episode.title?this.props.episode.title:'TBA'}
                </div>
                <div className="meta">
                    {this.renderEpisodeNumber()}
                    <strong> · </strong>
                    {this.renderAirDate()}
                </div>
                <div className="button-bar">
                    <WatchedButton 
                        showId={this.props.showId}
                        episodeNumber={this.props.episode.number}
                        watched={this.props.episode.user_watched}
                    />
                    <div 
                        className="play-button float-right"
                        onClick={this.onPlayClick}
                    >
                        <i className="fas fa-play-circle"></i>
                    </div>
                </div>
            </div>
        );
    }
}
EpisodeListItem.propTypes = propTypes;
EpisodeListItem.defaultProps = defaultProps;

export default EpisodeListItem;