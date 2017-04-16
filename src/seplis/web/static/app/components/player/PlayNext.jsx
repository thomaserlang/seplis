import React from 'react';

const propTypes = {
    title: React.PropTypes.string,
    description: React.PropTypes.string,
    url: React.PropTypes.string,
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
                className="fa fa-step-forward"
                title={this.props.title}
                href={this.props.url}
            />
        )
    }

}
PlayNext.propTypes = propTypes;

export default PlayNext;