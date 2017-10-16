import React from 'react';
import PropTypes from 'prop-types';
import Fecha from 'fecha';
import {request} from 'api';
import {dateInDays} from 'utils';

import './LatestEpisodesSideBar.scss';

const propTypes = {
    showId: PropTypes.number.isRequired,
    numberOfEpisodes: PropTypes.number,
}

const defaultProps = {
    numberOfEpisodes: 3,
}

class LatestEpisodesSideBar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            episodes: [],
        }
        this.getEpisodes();
    }

    renderEpisodeNumber(episode) {
        if (episode.episode) {
            return (
                <span>
                    S{episode.season} · E{episode.episode}
                    &nbsp;
                    ({episode.number})
                </span>
            )
        } else {
            return (
                <span>Episode {episode.number}</span>
            )   
        }
    }

    getEpisodes() {
        let dateUTC = Fecha.format(new Date().getTime(), 'YYYY-MM-DD');
        request(`/1/shows/${this.props.showId}/episodes`, {
            query: {
                q: `air_date:[${dateUTC} TO *]`,
                per_page: this.props.numberOfEpisodes,
                sort: 'number:asc',
            }
        }).done((episodes) => {
            this.setState({episodes:episodes});
        });
    }

    renderCountdown(episode) {
        if (!episode.air_datetime)
            return '';
        let dt = new Date(episode.air_datetime);
        let m = dt-new Date().getTime();
        if (m > 0) {
            return ' · In '+dateInDays(episode.air_datetime);
        } else {
            return ' · '+dateInDays(episode.air_datetime)+' ago';     
        }
    }

    render() {
        if (this.state.episodes.length == 0) {
            return (
                <p className="text-muted">No ETA for new episodes.</p>
            )
        }
        return (
            <div className="latest-episodes-side-bar">
                {this.state.episodes.map((item, i) => (
                    <div key={item.number} className="item">
                        <p>{item.title}</p>
                        <p>{this.renderEpisodeNumber(item)}</p>
                        <p>{item.air_date} {this.renderCountdown(item)}</p>
                    </div>
                ))}
            </div>
        )
    }
}
LatestEpisodesSideBar.propTypes = propTypes;
LatestEpisodesSideBar.defaultProps = defaultProps;

export default LatestEpisodesSideBar;