import React from 'react';
import {Link} from 'react-router-dom'
import {requireAuthed} from 'utils';

class Account extends React.Component {

    constructor(props) {
        super(props);
        requireAuthed();
    }

    render() {
        return (
            <div className="row">
                <div className="col-12">
                    <h1>Account</h1>
                </div>
                <div className="col-12">
                    <Link to="/password">Change password</Link>
                </div>
            </div>
        )
    }
}

export default Account;