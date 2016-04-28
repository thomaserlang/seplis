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
                    {this.props.episode.episode}
                    &nbsp;
                    <font color="grey">
                        {this.props.episode.number}
                    </font> 
                </span>
            )
        } else {
            return (
                <span>{this.props.episode.number}</span>
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
                </div>
            </div>
        );
    }
}

EpisodeListItem.propTypes = propTypes;

export default EpisodeListItem;