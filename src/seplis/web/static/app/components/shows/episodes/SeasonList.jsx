import React from 'react';
import ReactDOM from 'react-dom';
import request from 'api';

import ListItem from './ListItem';

class SeasonList extends React.Component {
    constructor(props) {
        super(props);
        this.episode = {
            title: "asd"
        }
    }

    render() {
        return (
            <div>
                Hello

                <ListItem episode={this.episode} />
            </div>
        );
    }
}

export default SeasonList;