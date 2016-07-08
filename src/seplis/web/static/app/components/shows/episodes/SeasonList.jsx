import React from 'react';
import ReactDOM from 'react-dom';
import {request} from 'api';
import {isAuthed} from 'utils';
import $ from 'jquery';

import './SeasonList.scss'
import EpisodeListItem from './EpisodeListItem';
import WatchedProgression from './WatchedProgression';
import SelectSeason from './SelectSeason';

const propTypes = {
    'showId': React.PropTypes.number.isRequired,
    'seasons': React.PropTypes.array.isRequired,
    'seasonNumber': React.PropTypes.number.isRequired,
}

class SeasonList extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            episodes: [],
            seasonNumber: this.props.seasonNumber,
        }
        this.onSeasonChange = this.onSeasonChange.bind(this);
    }

    componentDidMount() {
        this.getEpisodes();        
    }

    getEpisodes() {
        var position = $(window).scrollTop();
        this.setState({episodes: []});
        let season = this.seasonEpisodeNumbers(this.state.seasonNumber);
        let query = {}
        query.q = `number:[${season.from} TO ${season.to}]`;
        query.per_page = season.total;
        if (isAuthed()) {
            query.append = 'user_watched';
        }
        request(`/1/shows/${this.props.showId}/episodes`, {
            query: query,
        }).success((episodes) => {
            this.setState({episodes: episodes}, () => {
                $(window).scrollTop(position);
            });            
        });
    }

    seasonEpisodeNumbers(seasonNumber) {
        for (var s of this.props.seasons) {
            if (s.season == seasonNumber) {
                return s;
            }
        }
        return null;
    }

    onSeasonChange(e) {
        this.setState(
            {seasonNumber: parseInt(e.target.value)}, 
            ()=> {
                this.getEpisodes();
            }
        );
    }

    render() {
        return (
            <div className="show-season-list">
                <SelectSeason                    
                    seasons={this.props.seasons}
                    selectedSeason={this.state.seasonNumber}
                    onChange={this.onSeasonChange}
                />
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