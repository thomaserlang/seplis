import React from 'react';
import {request} from 'api'
import {isAuthed} from 'utils';

import EpisodeListItem from './EpisodeListItem';

const propTypes = {
    'showId': React.PropTypes.number.isRequired,
}

class EpisodeLastWatched extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            episode: null,
        }
        this.get();
    }

    get() {
        if (!isAuthed())
            return;
        request(
            `/1/shows/${this.props.showId}/episodes/last-watched`
        ).success(episode => {
            this.setState({episode: episode});
        })
    }

    render() {
        if (!this.state.episode)
            return <p className="text-muted">No episodes has been watched</p>;
        
        return (
            <EpisodeListItem 
                showId={this.props.showId}
                episode={this.state.episode}
                displaySeason={true}
            />
        );
    }

}
EpisodeLastWatched.propTypes = propTypes;

export default EpisodeLastWatched;