import React from 'react';
import PropTypes from 'prop-types';
import ClassNames from 'classnames'; 
import {getUserId} from 'utils';
import {request} from 'api';
import {trigger_episode_watched_status} from 'seplis/events';

import 'bootstrap/js/src/dropdown';
import './WatchedButton.scss';

const propTypes = {
    showId: PropTypes.number.isRequired,
    episodeNumber: PropTypes.number.isRequired,
    watched: PropTypes.object,
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
        }).done((data) => {
            trigger_episode_watched_status(
                'incr', 
                this.props.showId, 
                this.props.episodeNumber
            );
            this.setState(data);
        }).fail(() => {            
            this.setState({times: --this.state.times});
        });
    }    
    onWatchedDecr(e) {
        if (this.state.position > 0) {
            request(this.watchedApiEndpoint()
                .replace('watched', 'position'), {
                method: 'DELETE', 
            }).done((data) => {
                trigger_episode_watched_status(
                    'decr', 
                    this.props.showId, 
                    this.props.episodeNumber
                );
                this.setState({position: 0});
            });
        } else if (this.state.times > 0) { 
            this.setState({times: --this.state.times});
            request(this.watchedApiEndpoint(), {
                data: {times: -1},
                method: 'PUT', 
            }).done((data) => {
                trigger_episode_watched_status(
                    'decr', 
                    this.props.showId, 
                    this.props.episodeNumber
                );
                if (data) {
                    this.setState(data);
                } else {
                    this.setState({
                        times: 0,
                        position: 0,
                    });
                }
            }).fail(() => {            
                this.setState({times: ++this.state.times});
            });
        }
    }
    onWatchedClick(e) {
        if ((this.state.times > 0) || (this.state.position > 0))
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
        let dropdown = (this.state.times>0) || (this.state.position>0);
        let btnClass = ClassNames({
            btn: true,
            'btn-watched': true,
            watched: this.state.times>0,
            watching: this.state.position>0,
            'watching-watched': this.state.position>0 && this.state.times>0,
        });
        return (
            <div className="btn-group btn-episode-watched-group dropdown">
                {this.renderDropdown()}
                <button 
                    className={btnClass}
                    data-toggle={dropdown?'dropdown':'none'}
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