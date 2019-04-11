import React from 'react'
import PropTypes from 'prop-types'
import {NavLink} from 'react-router-dom'

import './ShowNav.scss'

let propTypes = {
    showId: PropTypes.number.isRequired,
}

class ShowNav extends React.Component {

    render() {
        return (
            <ul className="nav nav-tabs col-margin nav-seplis">
                <li className="nav-item">
                    <NavLink 
                        className="nav-link"       
                        exact                 
                        to={`/show/${this.props.showId}`}
                        activeClassName="active"
                    >
                        Main
                    </NavLink>
                </li>
                <li className="nav-item">
                    <NavLink 
                        className="nav-link" 
                        to={`/show/${this.props.showId}/info`}
                        activeClassName="active"
                    >
                        Info
                    </NavLink>
                </li>
                <li className="nav-item">
                    <NavLink 
                        className="nav-link" 
                        to={`/show/${this.props.showId}/seasons`}
                        activeClassName="active"
                    >
                        Seasons
                    </NavLink>
                </li>
                <li className="nav-item">
                    <NavLink 
                        className="nav-link" 
                        to={`/show/${this.props.showId}/stats`}
                        activeClassName="active"
                    >
                        Stats
                    </NavLink>
                </li>
                <li className="nav-item ml-auto">
                    <NavLink 
                        className="nav-link" 
                        to={`/show/${this.props.showId}/edit`}
                        activeClassName="active"
                    >
                        <i className="fas fa-cog"></i>
                    </NavLink>
                </li>
            </ul>
        )
    }
}
ShowNav.propTypes = propTypes

export default ShowNav