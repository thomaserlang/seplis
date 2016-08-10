import React from 'react';
import {getUserId} from 'utils';
import {request} from 'api';
import ShowList from './List';

const propTypes = {
    amount: React.PropTypes.number,
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
                <h2>Recently watched</h2>     
                <ShowList 
                    shows={this.state.shows} 
                    class="col-margin col-xs-4 col-sm-3 col-md-2"
                />
            </span>
        )
    }
}
RecentlyWatched.propTypes = propTypes;
RecentlyWatched.defaultProps = defaultProps;

export default RecentlyWatched;