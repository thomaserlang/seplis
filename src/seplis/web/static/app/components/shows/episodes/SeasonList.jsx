import React from 'react';
import ReactDOM from 'react-dom';
import {request} from 'api';
import {isAuthed} from 'utils';

import './SeasonList.scss'
import EpisodeListItem from './EpisodeListItem';
import WatchedProgression from './WatchedProgression';

const propTypes = {
    'showId': React.PropTypes.number.isRequired,
    'seasons': React.PropTypes.array.isRequired,
    'seasonNumber': React.PropTypes.number.isRequired,
}

class SeasonList extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            'episodes': [],
            'seasonNumber': this.props.seasonNumber,
        }
    }

    componentDidMount() {
        this.getEpisodes();        
    }

    getEpisodes() {
        this.state.episodes = [];
        this.setState(this.state);
        let season = this.seasonEpisodeNumbers(this.state.seasonNumber);
        let query = {}
        query.q = `number:[${season.from} TO ${season.to}]`;
        if (isAuthed()) {
            query.append = 'user_watched';
        }
        request(`/1/shows/${this.props.showId}/episodes`, {
            query: query,
        }).success((episodes) => {
            this.state.episodes = episodes;
            this.setState(this.state);            
        });
    }

    seasonEpisodeNumbers(seasonNumber) {
        for (var s of this.props.seasons) {
            if (s['season'] == seasonNumber) {
                return s;
            }
        }
        return null;
    }

    render() {
        return (
            <div className="show-season-list">
                <WatchedProgression 
                    showId={this.props.showId}
                    seasons={this.props.seasons}
                />
                <div className="episodes">
                    {this.state.episodes.map((item, index) => (
                        <EpisodeListItem 
                            key={item.number} 
                            showId={this.props.showId}
                            episode={item} 
                        />
                    ))}
                </div>
            </div>
        );
    }
}

SeasonList.propTypes = propTypes;

export default SeasonList;