import React from 'react';

import 'bootstrap/js/dropdown';
import './WatchedButton.scss';

const propTypes = {
    'count': React.PropTypes.number.isRequired,
}

class WatchedButton extends React.Component {
    render() {
        return (
            <div className="btn-group dropdown">
                <button className="btn">
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