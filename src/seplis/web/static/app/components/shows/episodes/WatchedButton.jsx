import React from 'react';
import ClassNames from 'classnames'; 
import {getUserId} from 'utils';
import {request} from 'api';
import {trigger_episode_watched_status} from 'seplis/events';

import 'bootstrap/js/dist/dropdown';
import './WatchedButton.scss';

const propTypes = {
    showId: React.PropTypes.number.isRequired,
    episodeNumber: React.PropTypes.number.isRequired,
    watched: React.PropTypes.object,
}

class WatchedButton extends React.Component {

    constructor(props) {
        super(props);
        this.setWatchedState();
        this.onWatchedIncr = this.onWatchedIncr.bind(this);
        this.onWatchedDecr = this.onWatchedDecr.bind(this);
        this.onWatchedClick = this.onWatchedClick.bind(this);
    }

    setWatchedState() {
        if (this.props.watched) {
            this.state = this.props.watched;
        } else {            
            this.state = {
                times: 0,
                position: 0,
            }
        }
    }

    watchedApiEndpoint() {
        let id = this.props.showId;
        let n = this.props.episodeNumber;
        return `/1/shows/${id}/episodes/${n}/watched`;
    }
    onWatchedIncr(e) {
        this.setState({times: ++this.state.times});
        request(this.watchedApiEndpoint(), {
            method: 'PUT', 
        }).success(() => {
            trigger_episode_watched_status(
                'incr', 
                this.props.showId, 
                this.props.episodeNumber
            );
        }).error(() => {            
            this.setState({times: --this.state.times});
        });
    }    
    onWatchedDecr(e) {
        if (this.state.times === 0) 
            return;
        this.setState({times: --this.state.times});
        request(this.watchedApiEndpoint(), {
            data: {times: -1},
            method: 'PUT', 
        }).success(() => {
            trigger_episode_watched_status(
                'decr', 
                this.props.showId, 
                this.props.episodeNumber
            );
        }).error(() => {            
            this.setState({times: ++this.state.times});
        });
    }
    onWatchedClick(e) {
        if (this.state.times !== 0) 
            return;
        this.onWatchedIncr(e);
    }

    renderDropdown() {
        return (
            <ul 
                className="dropdown-menu dropdown-menu-right" 
                role="menu"
            >
                <li onClick={this.onWatchedIncr}>
                    <i className="fa fa-plus"></i>
                </li>
                <li onClick={this.onWatchedDecr}>
                    <i className="fa fa-minus"></i>
                </li>
            </ul>
        )
    }

    render() {
        let btnClass = ClassNames({
            btn: true,
            'btn-watched': true,
            watched: this.state.times>0,
        });
        return (
            <div className="btn-group btn-episode-watched-group dropdown">
                {this.renderDropdown()}
                <button 
                    className={btnClass}
                    data-toggle={this.state.times>0?'dropdown':''}
                    onClick={this.onWatchedClick}
                >
                    Watched 
                </button>
                <button className="btn btn-times">
                    {this.state.times} 
                </button>
            </div>
        );
    }
}

WatchedButton.propTypes = propTypes;

export default WatchedButton;