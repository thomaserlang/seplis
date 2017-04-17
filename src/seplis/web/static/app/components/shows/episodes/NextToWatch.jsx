import React from 'react';
import {request} from 'api';
import {isAuthed} from 'utils';
import EpisodeListItem from './EpisodeListItem';
import {EVENT_EPISODE_WATCHED_STATUS} from 'seplis/events';

const propTypes = {
    showId: React.PropTypes.number.isRequired,
}

class NextToWatch extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            episode: null,
        }
        this.get();
        this.eventGet = this.get.bind(this);
        document.addEventListener(EVENT_EPISODE_WATCHED_STATUS, this.eventGet);
    }

    componentWillUnmount() {
        document.removeEventListener(EVENT_EPISODE_WATCHED_STATUS, this.eventGet);
    }

    get(event={}) {
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