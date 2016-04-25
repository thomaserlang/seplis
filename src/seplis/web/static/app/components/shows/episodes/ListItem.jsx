import React from 'react';

import './ListItem.scss';
import WatchedButton from './WatchedButton';

const propTypes = {
    episode: React.PropTypes.object.isRequired,
}

class ListItem extends React.Component {
    render() {
        return (
            <div>{this.props.episode.title}</div>
        );
    }
}

ListItem.propTypes = propTypes;

export default ListItem;