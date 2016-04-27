import React from 'react';
import ReactDOM from 'react-dom';
import {request} from 'api';

import './SeasonList.scss'
import EpisodeListItem from './EpisodeListItem';

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
        request(`/1/shows/${this.props.showId}/episodes`, {
            query: {
                q: `number:[${season.from} TO ${season.to}]`,
            },
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
                <div className="episodes">
                    {this.state.episodes.map((item, index) => (
                        <EpisodeListItem key={item.number} episode={item} />
                    ))}
                </div>
            </div>
        );
    }
}

SeasonList.propTypes = propTypes;

export default SeasonList;