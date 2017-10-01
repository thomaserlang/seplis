import React from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';

import './ShowNav.scss';

let propTypes = {
    showId: PropTypes.number.isRequired,
}

class ShowNav extends React.Component {

    render() {
        return (
            <ul className="nav nav-tabs col-margin nav-seplis">
                <li className="nav-item">
                    <Link 
                        className="nav-link"                        
                        to={`/show/${this.props.showId}/main`}
                        activeClassName="active"
                    >
                        Main
                    </Link>
                </li>
                <li className="nav-item">
                    <Link 
                        className="nav-link" 
                        to={`/show/${this.props.showId}/info`}
                        activeClassName="active"
                    >
                        Info
                    </Link>
                </li>
                <li className="nav-item">
                    <Link 
                        className="nav-link" 
                        to={`/show/${this.props.showId}/seasons`}
                        activeClassName="active"
                    >
                        Seasons
                    </Link>
                </li>
                <li className="nav-item">
                    <Link 
                        className="nav-link" 
                        to={`/show/${this.props.showId}/stats`}
                        activeClassName="active"
                    >
                        Stats
                    </Link>
                </li>
                <li className="nav-item ml-auto">
                    <Link 
                        className="nav-link" 
                        to={`/show/${this.props.showId}/edit`}
                        activeClassName="active"
                    >
                        <i className="fa fa-cog"></i>
                    </Link>
                </li>
            </ul>
        );
    }
}
ShowNav.propTypes = propTypes;

export default ShowNav;