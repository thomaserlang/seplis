import React from 'react'
import PropTypes from 'prop-types'
import {NavLink} from 'react-router-dom'
import {getUserLevel} from 'seplis/utils'

let propTypes = {
    movieId: PropTypes.number.isRequired,
}

class MovieNav extends React.Component {

    renderSettings() {
        if (getUserLevel() < 2) 
            return
        return (
            <NavLink 
                className="nav-link" 
                to={`/movie/${this.props.movieId}/edit`}
                activeClassName="active"
            >
                <i className="fas fa-cog"></i>
            </NavLink>
        )
    }

    render() {
        return (
            <nav className="nav nav-pills mb-3" style={{borderBottom:'1px solid #007bff'}}>
                <NavLink 
                    className="nav-link"       
                    exact                 
                    to={`/movie/${this.props.movieId}`}
                    activeClassName="active"
                >
                    Info
                </NavLink>
                {this.renderSettings()}
            </nav>
        )
    }
}
MovieNav.propTypes = propTypes

export default MovieNav