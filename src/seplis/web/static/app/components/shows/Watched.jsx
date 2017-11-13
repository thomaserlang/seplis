import React from 'react';
import PropTypes from 'prop-types';
import {getUserId, episodeNumber} from 'utils';
import {request} from 'api';

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
        getWatched(this.props.perPage, this.props.page).then((data) => {
            this.setState({shows: data.items});
        });
    }

    renderShow(show, episode) {
        return (
            <div key={show.id} className="col-4 col-md-3 col-lg-2 col-margin">
                <a href={`/show/${show.id}`}>
                    <img 
                        title={show.title}
                        alt={show.title}
                        src={show.poster_image!=null?show.poster_image.url + '@SX180':''} 
                        className="img-fluid"
                    />
                </a>
                <div className="black-box">{episodeNumber(show, episode)}</div>
            </div>
        )
    }

    render() {
        if (this.state.shows.length == 0) 
            return (
                <div className="alert alert-info">
                    You have not watched any shows yet!
                </div>
            );
        return (
            <div className="row">
                {this.state.shows.map(item => (
                    this.renderShow(item, item.user_watching.episode)
                ))}
            </div>
        )
    }
}
Watched.propTypes = propTypes;
Watched.defaultProps = defaultProps;

export default Watched;

export function getWatched(perPage, page) {
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