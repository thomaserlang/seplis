import React from 'react';
import {request} from 'api';

import EpisodeListItem from './EpisodeListItem';

const propTypes = {
    showId: React.PropTypes.number.isRequired,
    numberOfEpisodes: React.PropTypes.number,
}

const defaultProps = {
    numberOfEpisodes: 3,
}

class NextToWatchList extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            episodes: [],
        }
        this.getEpisodes();
    }

    getEpisodes() {
        request(
            `/1/shows/${this.props.showId}/episodes/to-watch`
        ).success(episode => {
            request(`/1/shows/${this.props.showId}/episodes`, {
                query: this.queryFromEpisode(episode),
            }).success(episodes => {
                this.setState({episodes:episodes});
            });
        }).error(error => {
            // No more episodes to watch
            if (error.responseJSON.code === 1301) {
                this.setState({episodes:[]});
            }
        });
    }

    queryFromEpisode(episode) {
        let fromNumber = episode.number;
        return {
            q: `number:[${fromNumber} TO ${(fromNumber-1) + this.props.numberOfEpisodes}]`,
            sort: 'number:asc',
            append: 'user_watched',
        }
    }

    render() {
        return (
            <span>
            {this.state.episodes.map((item, key) => (
                <EpisodeListItem 
                    key={item.number}
                    showId={this.props.showId}
                    episode={item}
                />
            ))}
            </span>
        )
    }
}
NextToWatchList.propTypes = propTypes;
NextToWatchList.defaultProps = defaultProps;

export default NextToWatchList;