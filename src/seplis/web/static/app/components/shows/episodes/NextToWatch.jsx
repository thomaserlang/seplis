import React from 'react';
import {request} from 'api';
import {isAuthed} from 'utils';
import EpisodeListItem from './EpisodeListItem';

const propTypes = {
    showId: React.PropTypes.number.isRequired,
}

class NextToWatch extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            episode: null,
        }
        document.addEventListener('episode/watched-status-changed', this.get);
        this.get();
    }

    get() {
        if (!isAuthed()) {
            request(
                `/1/shows/${this.props.showId}/episodes/1`
            ).success(episode => {
                this.setState({episode: episode});
            });
            return;
        }

        request(
            `/1/shows/${this.props.showId}/episodes/to-watch`
        ).success(episode => {
            this.setState({episode: episode});
        }).error(error => {
            // No more episodes to watch
            if (error.responseJSON.code === 1301) {
                this.setState({episode: null});
            }
        });
    }

    render() {
        if (this.state.episode == null) {
            return <p className="text-muted">No episodes to watch</p>;
        }
        return (
            <EpisodeListItem 
                key={this.state.episode.number}
                showId={this.props.showId}
                episode={this.state.episode}
                displaySeason={true}
            />
        )
    }
}
NextToWatch.propTypes = propTypes;

export default NextToWatch;