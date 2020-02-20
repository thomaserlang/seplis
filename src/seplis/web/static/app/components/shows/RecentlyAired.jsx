import React from 'react'
import PropTypes from 'prop-types'
import {getUserId, episodeNumber} from 'utils'
import {request} from 'api'

import './List.scss'

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

class RecentlyAired extends React.Component {

    constructor(props) {
        super()
        this.state = {
            items: [],
        }
    }

    componentDidMount() {
        if (!this.props.items) {
            this.getData()
        } else {
            this.setState({items: this.props.items})
        }
    }

    getData() {
        getRecentlyAired(this.props.perPage, this.props.page).then((data) => {
            this.setState({items: data.items})
        })
    }

    renderItem(item) {
        let show = item.show
        let episode = item.episode
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
        if (this.state.items.length == 0)
            return (
                <div className="alert alert-info">
                    No recently aired episodes from shows you're following.
                </div>
            )
        return (
            <div className="row">
                {this.state.items.map(item => (
                    this.renderItem(item)
                ))}
            </div>
        )
    }
}
RecentlyAired.propTypes = propTypes
RecentlyAired.defaultProps = defaultProps

export default RecentlyAired

export function getRecentlyAired(perPage, page) {
    return new Promise((resolve, reject) => {
        request(`/1/users/${getUserId()}/shows-recently-aired`, {
            query: {
                'per_page': perPage,
                page: page,
            },
        }).done((data, textStatus, jqXHR) => {
            resolve({items: data, jqXHR: jqXHR})
        }).fail((e) => {
            reject(e)
        })
    })
}