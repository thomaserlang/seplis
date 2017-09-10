import React from 'react';
import PropTypes from 'prop-types';
import ReactDOM from 'react-dom';
import {request} from 'api';
import {isAuthed} from 'utils';
import $ from 'jquery';

import EpisodeListItem from './EpisodeListItem';
import WatchedProgression from './WatchedProgression';
import SelectSeason from './SelectSeason';

const propTypes = {
    'showId': PropTypes.number.isRequired,
    'seasons': PropTypes.array.isRequired,
    'seasonNumber': PropTypes.number.isRequired,
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
        if (this.props.seasons.length < 1) 
            return;
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
        }).done((episodes) => {
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
        if (this.props.seasons.length < 1) 
            return (
                <div className="alert alert-warning">
                    <strong>This show has 0 episodes.</strong>  
                </div>
            );
        return (
            <span>
            <div className="row">
                <div className="col-12 col-sm-auto ml-auto order-md-12 mb-2 mb-md-0">
                    <div className="float-right">
                        <WatchedProgression 
                            showId={this.props.showId}
                            seasons={this.props.seasons}
                        />
                    </div>
                </div>
                <div className="col-12 col-md-4">
                    <SelectSeason                    
                        seasons={this.props.seasons}
                        selectedSeason={this.state.seasonNumber}
                        onChange={this.onSeasonChange}
                    />
                </div>
            </div>
            <div className="row show-season-list">
                <div className="col-12 d-md-none col-margin" />
                <div className="col-12">
                    <div className="row">
                        {this.state.episodes.map((item, index) => (
                            <div                            
                                key={item.number} 
                                className="col-12 col-md-6 col-lg-4"
                            >
                                <div className="d-none d-md-block col-margin" />
                                <EpisodeListItem 
                                    showId={this.props.showId}
                                    episode={item} 
                                />
                            </div>
                        ))}
                    </div>
                </div>
            </div>
            </span>
        );
    }
}

SeasonList.propTypes = propTypes;

export default SeasonList;