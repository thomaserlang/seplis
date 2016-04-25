import React from 'react';

import 'bootstrap/js/dropdown';
import './watched_button.scss';

const WatchedButton = React.createClass({
    propTypes: {
        value: React.PropTypes.number.isRequired,
    },

    render() {
        return (
            <div className="btn-group dropdown">
                <button className="btn">
                    Watched 
                </button>
                <button className="btn">
                    {this.props.value} 
                </button>
            </div>
        );
    }
});

export default WatchedButton;