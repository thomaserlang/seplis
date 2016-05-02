import React from 'react';
import {request} from 'api';
import {isAuthed} from 'utils';

import Loader from '../components/Loader';

const propTypes = {
    showId: React.PropTypes.number.isRequired,
}

class Show extends React.Component {

    constructor(props) {
        super(props);
        this.state = {};
        this.getShow();
    }

    getShow() {
        let query = {};
        if (isAuthed()) {
            query.append = 'is_fan';
        }
        request(`/1/shows/${this.props.showId}`, {
            query: query,
        }).success(show => {
            this.setState({show: show});
        });
    }

    render() {
        let show = this.state.show;
        let style = {"marginTop": "20px"}
        return (
            <Loader />
        )
    }
}
Show.propTypes = propTypes;

export default Show;