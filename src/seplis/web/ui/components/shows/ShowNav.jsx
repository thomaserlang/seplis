import React from 'react'
import PropTypes from 'prop-types'
import {NavLink} from 'react-router-dom'
import UserRating from 'seplis/components/shows/UserRating'
import {getUserLevel, isAuthed} from 'seplis/utils'

let propTypes = {
    showId: PropTypes.number.isRequired,
}

class ShowNav extends React.Component {

    renderSettings() {
        if (getUserLevel() < 2) 
            return
        return (
            <NavLink 
                className="nav-link" 
                to={`/show/${this.props.showId}/edit`}
                activeClassName="active"
            >
                <i className="fas fa-cog"></i>
            </NavLink>
        )
    }

    renderRating(showId) {
        if (isAuthed()) 
            return <div className="ml-auto">
                <UserRating showId={this.props.showId} />
            </div>
    }

    render() {
        return (
            <nav className="nav nav-pills mb-3" style={{borderBottom:'1px solid #007bff'}}>
                <NavLink 
                    className="nav-link"       
                    exact                 
                    to={`/show/${this.props.showId}`}
                    activeClassName="active"
                >
                    Main
                </NavLink>
                <NavLink 
                    className="nav-link" 
                    to={`/show/${this.props.showId}/info`}
                    activeClassName="active"
                >
                    Info
                </NavLink>
                <NavLink 
                    className="nav-link" 
                    to={`/show/${this.props.showId}/seasons`}
                    activeClassName="active"
                >
                    Seasons
                </NavLink>
                <NavLink 
                    className="nav-link" 
                    to={`/show/${this.props.showId}/images`}
                    activeClassName="active"
                >
                    Images
                </NavLink>
                <NavLink 
                    className="nav-link" 
                    to={`/show/${this.props.showId}/stats`}
                    activeClassName="active"
                >
                    Stats
                </NavLink>
                {this.renderRating()}
                {this.renderSettings()}
            </nav>
        )
    }
}
ShowNav.propTypes = propTypes

export default ShowNav