import React from 'react';
import PropTypes from 'prop-types';
import {request} from 'api';
import {isAuthed} from 'utils';
import EpisodeListItem from './EpisodeListItem';
import {EVENT_EPISODE_WATCHED_STATUS} from 'seplis/events';

const propTypes = {
    showId: PropTypes.number.isRequired,
}

class NextToWatch extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            episode: null,
        }
        this.eventGet = this.get.bind(this);
        document.addEventListener(EVENT_EPISODE_WATCHED_STATUS, this.eventGet);
        document.addEventListener('visibilitychange', this.eventGet);
    }
    
    componentDidMount() {
        this.get();        
    }

    componentWillUnmount() {
        document.removeEventListener(EVENT_EPISODE_WATCHED_STATUS, this.eventGet);
        document.removeEventListener('visibilitychange', this.eventGet);
    }

    get(event={}) {
        if (document.hidden) return;
        if (!isAuthed()) {
            request(
                `/1/shows/${this.props.showId}/episodes/1`
            ).done(episode => {
                this.setState({episode: episode});
            });
            return;
        }

        request(
            `/1/shows/${this.props.showId}/episodes/to-watch`
        ).done(episode => {
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