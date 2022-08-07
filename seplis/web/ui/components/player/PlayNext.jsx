import React from 'react';
import PropTypes from 'prop-types';

const propTypes = {
    title: PropTypes.string,
    description: PropTypes.string,
    url: PropTypes.string,
}

class PlayNext extends React.Component {

    constructor(props) {
        super(props);
        this.onNextClick = this.nextClick.bind(this);
    }

    nextClick(e) {
        location.href = this.props.url;
    }

    render() {
        return (
            <a 
                title={this.props.title}
                href={this.props.url}
            >
                <i className="fas fa-step-forward" />
            </a>
        )
    }

}
PlayNext.propTypes = propTypes;

export default PlayNext;