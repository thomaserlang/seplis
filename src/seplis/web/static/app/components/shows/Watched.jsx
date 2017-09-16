import React from 'react';
import PropTypes from 'prop-types';
import {getUserId} from 'utils';
import {request} from 'api';
import ShowList from './List';

const propTypes = {
    perPage: PropTypes.number,
    page: PropTypes.number,
    items: PropTypes.array,
}

const defaultProps = {
    perPage: 6,
    page: 1,
    items: null,
}

class Watched extends React.Component {

    constructor(props) {
        super();
        this.state = {
            shows: [],
        }
    }

    componentDidMount() {
        if (!this.props.items) {
            this.getData();
        } else {
            this.setState({shows: this.props.items});
        }
    }

    getData() {
        getItems(this.props.perPage, this.props.page).then((data) => {
            this.setState({shows: data.items});
        });
    }

    render() {
        if (this.state.shows.length == 0) 
            return (
                <div className="alert alert-info">
                    You have not watched any shows yet!
                </div>
            );
        return (
            <ShowList shows={this.state.shows} />
        )
    }
}
Watched.propTypes = propTypes;
Watched.defaultProps = defaultProps;

export default Watched;

export function getItems(perPage, page) {
    return new Promise((resolve, reject) => {
        request(`/1/users/${getUserId()}/shows-watched`, {
            query: {
                'per_page': perPage,
                page: page,
            },
        }).done((data, textStatus, jqXHR) => {
            resolve({items: data, jqXHR: jqXHR});
        }).fail((e) => {
            reject(e);
        })
    })
}