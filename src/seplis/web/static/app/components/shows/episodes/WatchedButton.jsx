import React from 'react';

import 'bootstrap/js/dropdown';
import './WatchedButton.scss';

const propTypes = {
    'count': React.PropTypes.number.isRequired,
}

class WatchedButton extends React.Component {

    renderDropdown() {
        return (
            <ul 
                className="
                    dropdown-menu  
                    dropdown-menu-right
                    btn-watched-button-dropdown
                " 
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
            <div className="btn-group dropdown">
                {this.renderDropdown()}
                <button 
                    className="btn"
                    data-toggle="dropdown"
                >
                    Watched 
                </button>
                <button className="btn">
                    {this.props.count} 
                </button>
            </div>
        );
    }
}

WatchedButton.propTypes = propTypes;

export default WatchedButton;