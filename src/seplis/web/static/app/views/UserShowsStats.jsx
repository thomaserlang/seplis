import React from 'react';
import Loader from 'components/Loader';
import {requireAuthed, getUserId} from 'utils';
import {request} from 'api';

class UserShowsStats extends React.Component {

    constructor(props) {
        super(props);
        requireAuthed();
        this.state = {
            loading: true,
            stats: null,
        }
    }

    componentDidMount() {
        this.getStats();
    }

    getStats() {
        let userId = getUserId();
        request(`/1/users/${userId}/show-stats`).done((stats) => {
            this.setState({
                loading: false,
                stats: stats,
            });
        });
    }

    render() {
        if (this.state.loading)
            return (
                <span>
                    <Loader />
                    <center><h2>Loading your stats</h2></center>
                </span>
            );
        return (
            <span>
            <h2>Your TV show stats</h2>
            <table className="table table-striped">
                <tr><th width="220px">Fan of</th>
                    <td>{this.state.stats.fan_of} shows</td></tr>
                <tr><th>Time spent watching</th>
                    <td>{Math.round(this.state.stats.episodes_watched_minutes/60)} hours</td></tr>
                <tr><th>Episodes watched</th>
                    <td>{this.state.stats.episodes_watched}</td></tr>
                <tr><th>Watched episodes from</th>
                    <td>{this.state.stats.shows_watched} shows</td></tr>
            </table>
            </span>
        )
    }
}

export default UserShowsStats;