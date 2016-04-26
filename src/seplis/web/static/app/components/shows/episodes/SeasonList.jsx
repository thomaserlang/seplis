import React from 'react';
import ReactDOM from 'react-dom';
import {request} from 'api';

import ListItem from './ListItem';

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
        request(`/api/shows/${this.props.showId}/episodes`, {
            'query': {
                'q': `number:[${season.from} TO ${season.to}]`,
            },
            success: (data) => {
                this.state.episodes = data.episodes;
                this.setState(this.state);
            },
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
        console.log('render');
        return (
            <div className="show-season-list">
                <div className="show-season-list__episodes">
                    {this.state.episodes.map((item, index) => (
                        <ListItem key={item.number} episode={item} />
                    ))}
                </div>
            </div>
        );
    }
}

SeasonList.propTypes = propTypes;

export default SeasonList;