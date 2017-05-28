import React from 'react';
import PropTypes from 'prop-types';
import Fecha from 'fecha';
import {request} from 'api';

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
        }).success((episodes) => {
            this.setState({episodes:episodes});
        });
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
                        {i == 0?<p className="next-episode">Next Episode</p>: ''}
                        <p>{item.title}</p>
                        <p>{this.renderEpisodeNumber(item)}</p>
                        <p>{item.air_date}</p>
                    </div>
                ))}
            </div>
        )
    }
}
LatestEpisodesSideBar.propTypes = propTypes;
LatestEpisodesSideBar.defaultProps = defaultProps;

export default LatestEpisodesSideBar;