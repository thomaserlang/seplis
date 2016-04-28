import React from 'react';
import {getUserId} from 'utils';
import {request} from 'api';

import 'bootstrap/js/dropdown';
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
        let userId = getUserId();
        return `/1/users/${userId}/watched/shows/${this.props.showId}/episodes/${this.props.episodeNumber}`;
    }
    onWatchedIncr(e) {
        this.setState({times: ++this.state.times});
        request(this.watchedApiEndpoint(), {
            method: 'PUT', 
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
        }).error(() => {            
            this.setState({times: ++this.state.times});
        });
    }

    renderDropdown() {
        return (
            <ul 
                className="dropdown-menu dropdown-menu-right" 
                role="menu"
            >
                <li onClick={this.onWatchedIncr}>
                    <i className="glyphicon glyphicon-plus"></i>
                </li>
                <li onClick={this.onWatchedDecr}>
                    <i className="glyphicon glyphicon-minus"></i>
                </li>
            </ul>
        )
    }

    render() {
        return (
            <div className="btn-group btn-episode-watched-group dropdown">
                {this.renderDropdown()}
                <button 
                    className="btn btn-watched"
                    data-toggle="dropdown"
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