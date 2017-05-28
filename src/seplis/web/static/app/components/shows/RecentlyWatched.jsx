import React from 'react';
import PropTypes from 'prop-types';
import {getUserId} from 'utils';
import {request} from 'api';
import ShowList from './List';

const propTypes = {
    amount: PropTypes.number,
}

const defaultProps = {
    amount: 6,
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
                'per_page': this.props.amount,
            },
        }).success(data => {
            this.setState({shows: data});
        });
    }


    render() {
        return (
            <span>
                <h2 className="header">Recently watched</h2>     
                <ShowList 
                    shows={this.state.shows} 
                    mobile_xscroll={true}
                />
            </span>
        )
    }
}
RecentlyWatched.propTypes = propTypes;
RecentlyWatched.defaultProps = defaultProps;

export default RecentlyWatched;