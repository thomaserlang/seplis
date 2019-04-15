import React from 'react';
import Loader from 'components/Loader';
import {requireAuthed, getUserId, secondsToPretty} from 'utils';
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
        document.title = `User Stats | SEPLIS`
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
                <tbody>
                <tr><th width="220px">Fan of</th>
                    <td>{this.state.stats.fan_of} shows</td></tr>
                <tr><th>Time spent watching</th>
                    <td>{secondsToPretty(this.state.stats.episodes_watched_minutes*60, true)}</td></tr>
                <tr><th>Episodes watched</th>
                    <td>{this.state.stats.episodes_watched}</td></tr>
                <tr><th>Watched episodes from</th>
                    <td>{this.state.stats.shows_watched} shows</td></tr>
                <tr><th>Shows finished</th>
                    <td>{this.state.stats.shows_finished}</td></tr>
                </tbody>
            </table>
            </span>
        )
    }
}

export default UserShowsStats;