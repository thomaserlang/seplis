import React from 'react';

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
        if (props.watched) {
            this.state = props.watched;
        } else {            
            this.state = {
                times: 0,
                position: 0,
            }
        }
    }

    renderDropdown() {
        return (
            <ul 
                className="dropdown-menu dropdown-menu-right" 
                role="menu"
            >
                <li>
                    <i className="glyphicon glyphicon-plus"></i>
                </li>
                <li>
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