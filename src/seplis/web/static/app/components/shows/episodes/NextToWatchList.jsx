import React from 'react';
import {request} from 'api';
import {isAuthed} from 'utils';
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
        if (!isAuthed()) {
            this.episodesFrom(1);
            return;
        }

        request(
            `/1/shows/${this.props.showId}/episodes/to-watch`
        ).success(episode => {
            this.episodesFrom(episode.number);
        }).error(error => {
            // No more episodes to watch
            if (error.responseJSON.code === 1301) {
                this.setState({episodes:[]});
            }
        });
    }

    episodesFrom(fromNumber) {
        let query = {
            q: `number:[${fromNumber} TO ${(fromNumber-1) + this.props.numberOfEpisodes}]`,
            sort: 'number:asc',
        }
        if (isAuthed()) {            
            query.append = 'user_watched';
        }
        request(`/1/shows/${this.props.showId}/episodes`, {
            query: query,
        }).success(episodes => {
            this.setState({episodes:episodes});
        });
    }

    render() {
        if (this.state.episodes.length == 0) {
            return <p className="text-muted">No episodes to watch</p>;
        }
        return (
            <span>
            {this.state.episodes.map((item, key) => (
                <EpisodeListItem 
                    key={item.number}
                    showId={this.props.showId}
                    episode={item}
                    displaySeason={true}
                />
            ))}
            </span>
        )
    }
}
NextToWatchList.propTypes = propTypes;
NextToWatchList.defaultProps = defaultProps;

export default NextToWatchList;