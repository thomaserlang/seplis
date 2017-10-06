import React from 'react';
import PropTypes from 'prop-types';

import './EpisodeListItem.scss';
import WatchedButton from './WatchedButton';

const propTypes = {
    showId: PropTypes.number.isRequired,
    episode: PropTypes.object.isRequired,
    displaySeason: PropTypes.bool,
}

const defaultProps = {
    displaySeason: true,
}

class EpisodeListItem extends React.Component {

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
                    <div className="float-right">
                        <a 
                            href={this.getPlayUrl()}
                            className="play-button"
                            data-type="episode"
                            data-show-id={this.props.showId}
                            data-episode-number={this.props.episode.number}
                        >
                            <i className="fa fa-play-circle"></i>
                        </a>
                    </div>
                </div>
            </div>
        );
    }
}
EpisodeListItem.propTypes = propTypes;
EpisodeListItem.defaultProps = defaultProps;

export default EpisodeListItem;