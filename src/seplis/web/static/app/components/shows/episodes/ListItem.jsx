import React from 'react';

import './ListItem.scss';
import WatchedButton from './WatchedButton';

const propTypes = {
    episode: react.PropTypes.object.isRequired,
}

class ListItem extends React.Component {
    render() {
        return <div>{episode.title}</div>
    }
}

ListItem.propTypes = propTypes;

export default ListItem;