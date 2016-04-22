import React from 'react';

require('bootstrap/js/dropdown');

const WatchedButton = React.createClass({
    propTypes: {
        value: React.PropTypes.any.isRequired
    },

    render() {
        return (
            <div class="btn-group dropdown">
                <button className="btn btn-warning">
                    Watched {this.props.value}
                </button>
            </div>
        );
    }
});

export default WatchedButton;