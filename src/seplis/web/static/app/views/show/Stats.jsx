import React from 'react';
import {request} from 'api';
import {isAuthed} from 'utils';

class Stats extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            userStats: null,
        }
    }

    componentDidMount() {
        if (isAuthed()) 
            this.getUserStats();
    }

    getUserStats() {
        request(`/1/shows/${this.props.show.id}/user-stats`).done((stats) => {
            this.setState({
                userStats: stats,
            });
        });
    }

    countEpisodes() {
        if (!this.props.show.seasons)
            return 0;
        let totalEpisodes = 0;
        for (let season of this.props.show.seasons) {
            totalEpisodes += season.total;
        }
        return totalEpisodes;
    }

    renderUserStats() {
        if (!this.state.userStats)
            return null;
        return (
            <span>
                <h2 className="mb-1 mt-3">Your stats</h2>
                <table className="table table-striped">
                    <tbody>
                    <tr><th width="200px">Episodes watched</th><td>{this.state.userStats.episodes_watched}</td></tr>
                    <tr><th>Time spent watching</th>
                        <td>{Math.round(((this.state.userStats.episodes_watched_minutes/60)*10))/10} hours</td></tr>
                    </tbody>
                </table>
            </span>
        )
    }

    render() {
        let episodeCount = this.countEpisodes();
        return (
            <span>
                {this.renderUserStats()}
                
                <h2 className="mb-1">Show stats</h2>
                <table className="table table-striped">
                    <tbody>
                    <tr><th width="200px">Total episodes</th><td>{episodeCount}</td></tr>
                    <tr><th>Hours worth of content</th>
                        <td>{Math.round(((this.props.show.runtime*episodeCount/60)*10))/10} hours</td></tr>
                    </tbody>
                </table>
            </span>
        )
    }

}

export default Stats;