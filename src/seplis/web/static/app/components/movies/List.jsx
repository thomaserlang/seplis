import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'
import {Link} from 'react-router-dom'

const propTypes = {
    movies: PropTypes.array.isRequired,
    mobile_xscroll: PropTypes.bool,
    listMode: PropTypes.string,
}

const defaultProps = {
    mobile_xscroll: false,
    listMode: 'grid',
}

class List extends React.Component {

    renderMovie(movie) {
        return <div key={movie.id} className="col-4 col-sm-4 col-md-3 col-lg-2 col-margin">
            <Link to={`/movie/${movie.id}`}>
                <img 
                    title={movie.title}
                    alt={movie.title}
                    src={movie.poster_image!=null?movie.poster_image.url + '@SX180':''} 
                    className="img-fluid"
                />
            </Link>
        </div>
    }

    renderGrid() {
        let c = ClassNames({
            row: true,
            'slider': this.props.mobile_xscroll,
        })
        return <div className={c}>
            {this.props.movies.map(movie => (
                this.renderMovie(movie)
            ))}
        </div>        
    }

    trClick = (e) => {
        location.href = `/movie/${e.currentTarget.dataset.movieid}`
    }

    renderListItem(movie) {
        return <tr key={movie.id} onClick={this.trClick} data-movieid={movie.id} className="pointer">
            <td><Link to={`/movie/${movie.id}`}>{movie.title}</Link></td>
            <td width="115px">{movie.release_date}</td>
        </tr>
    }

    renderList() {
        return <table className="table table-striped">
            <thead>
                <tr className="thead-dark">
                    <th>Title</th>
                    <th>Release date</th>
                </tr>
            </thead>
            <tbody>
                {this.props.movies.map(movie => (
                    this.renderListItem(movie)
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