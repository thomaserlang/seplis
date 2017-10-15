import React from 'react';
import {browserHistory} from 'react-router';
import SeasonList from 'components/shows/episodes/SeasonList';

class Seasons extends React.Component {

    constructor(props) {
        super(props);
        this.onSeasonChange = this.seasonChange.bind(this);
        let season = parseInt(this.props.location.query.season) || null;
        if (!season) {
            if (this.props.show.seasons.length > 0)
                season = this.props.show.seasons.slice(-1)[0].season;
        }
        this.state = {
            season: season,
        }
    }

    seasonChange(season) {
        this.setState({
            season: season,
        });
        browserHistory.push({
            pathname: this.props.location.pathname,
            query: { 
                season: season,
            },
        });
    }

    render() {
        return (
            <SeasonList
                key={this.state.season}
                showId={this.props.show.id}
                seasons={this.props.show.seasons}
                seasonNumber={this.state.season}
                onSeasonChange={this.onSeasonChange}
            />
        );
    }
}

export default Seasons;