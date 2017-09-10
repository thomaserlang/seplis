import React from 'react';
import PropTypes from 'prop-types';
import {getUserId} from 'utils';
import {request} from 'api';
import ShowList from './List';

const propTypes = {
    perPage: PropTypes.number,
}

const defaultProps = {
    perPage: 6,
}

class RecentlyWatched extends React.Component {

    constructor(props) {
        super();
        this.state = {
            shows: [],
        }
    }

    componentDidMount() {
        this.getData();
    }

    getData() {
        request(`/1/users/${getUserId()}/shows-recently-watched`, {
            query: {
                'per_page': this.props.perPage,
            },
        }).done(data => {
            this.setState({shows: data});
        });
    }


    render() {
        return (
            <ShowList shows={this.state.shows} />
        )
    }
}
RecentlyWatched.propTypes = propTypes;
RecentlyWatched.defaultProps = defaultProps;

export default RecentlyWatched;