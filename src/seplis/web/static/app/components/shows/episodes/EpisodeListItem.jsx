import React from 'react';

import './EpisodeListItem.scss';
import WatchedButton from './WatchedButton';

const propTypes = {
    showId: React.PropTypes.number.isRequired,
    episode: React.PropTypes.object.isRequired,
}

class EpisodeListItem extends React.Component {

    renderEpisodeNumber() {
        if (this.props.episode.episode) {
            return (
                <span>
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
                <date 
                    className="air-date" 
                    title={this.props.episode.air_date}
                >
                    {this.props.episode.air_date}
                </date> 
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
                    {this.props.episode.title}
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
                    <div className="pull-right">
                        <a 
                            href={this.getPlayUrl()} 
                            className="play-button"
                        >
                            <i className="glyphicon glyphicon-play-circle"></i>
                        </a>
                    </div>
                </div>
            </div>
        );
    }
}

EpisodeListItem.propTypes = propTypes;

export default EpisodeListItem;