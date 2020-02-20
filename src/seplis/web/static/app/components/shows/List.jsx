import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'
import {Link} from 'react-router-dom'
import {episodeNumber} from 'utils'

import './List.scss'

const propTypes = {
    shows: PropTypes.array.isRequired,
    mobile_xscroll: PropTypes.bool,
    listMode: PropTypes.string,
}

const defaultProps = {
    mobile_xscroll: false,
    listMode: 'grid',
}

class List extends React.Component {

    renderShow(show) {
        return <div key={show.id} className="col-4 col-sm-4 col-md-3 col-lg-2 col-margin">
            <a href={`/show/${show.id}`}>
                <img 
                    title={show.title}
                    alt={show.title}
                    src={show.poster_image!=null?show.poster_image.url + '@SX180':''} 
                    className="img-fluid"
                />
            </a>
            {this.renderEpisode(show)}
        </div>
    }

    renderEpisode(show) {
        if ('user_watching' in show) {
            return <div className="black-box">
                {episodeNumber(show, show.user_watching.episode)}
            </div>
        }
    }

    renderGrid() {
        let c = ClassNames({
            row: true,
            'slider': this.props.mobile_xscroll,
        })
        return <div className={c}>
            {this.props.shows.map(show => (
                this.renderShow(show)
            ))}
        </div>        
    }

    trClick = (e) => {
        location.href = `/show/${e.currentTarget.dataset.showid}`
    }

    renderUserWatching(show) {
        if ('user_watching' in show) {
            return <>                
                <td>{episodeNumber(show, show.user_watching.episode)}</td>
                <td title={show.user_watching.watched_at}>{show.user_watching.watched_at.substring(0,10)}</td>
            </>
        }
    }

    renderUserWatchingHeader() {
        if (this.props.shows.length < 1)
            return null
        if ('user_watching' in this.props.shows[0]) {
            return <>
                <th width="115px" title="Latest watched episode">Episode</th>
                <th width="115px">Watched at</th>
            </>
        }
    }

    renderListItem(show) {
        return <tr key={show.id} onClick={this.trClick} data-showid={show.id} className="pointer">
            <td><a href={`/show/${show.id}`}>{show.title}</a></td>
            {this.renderUserWatching(show)}
            <td width="115px">{show.premiered}</td>
            <td width="10px" className="text-right">{show.user_rating}</td>
        </tr>
    }

    renderList() {
        return <table className="table table-striped">
            <thead>
                <tr className="thead-dark">
                    <th>Title</th>
                    {this.renderUserWatchingHeader()}
                    <th>Premiered</th>
                    <th className="text-right">Rating</th>
                </tr>
            </thead>
            <tbody>
                {this.props.shows.map(show => (
                    this.renderListItem(show)
                ))}
            </tbody>
        </table>
    }

    render() {
        let lm = this.props.listMode
        if (!lm) 
            lm = localStorage.getItem('listMode') || 'grid'
        if (lm == 'grid')
            return this.renderGrid()
        else 
            return this.renderList() 
    }
}
List.propTypes = propTypes
List.defaultProps = defaultProps

export default List