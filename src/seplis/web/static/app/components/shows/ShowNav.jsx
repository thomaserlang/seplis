import React from 'react';
import {Link} from 'react-router';

let propTypes = {
    showId: React.PropTypes.number.isRequired,
}

class ShowNav extends React.Component {

    render() {
        return (
            <ul className="nav nav-tabs col-margin">
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
                    <a className="nav-link" href="seasons">Seasons</a>
                </li>
            </ul>
        );
    }
}
ShowNav.propTypes = propTypes;

export default ShowNav;