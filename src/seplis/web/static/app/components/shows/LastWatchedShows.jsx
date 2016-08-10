import React from 'react';
import {getUserId} from 'utils';
import {request} from 'api';

class RecentlyWatched extends React.Component {

    componentDidMount() {

    }

    getData() {
        request(`/1/users/([0-9]+)/shows-recently-watched`)
    }


    render() {
        return (

        )
    }
}

export default RecentlyWatched;