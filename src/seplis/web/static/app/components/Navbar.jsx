import React from 'react';
import {request} from 'api';
import {isAuthed, getUserLevel} from 'utils';
import Search from './Search';

import './Navbar.scss';

class Navbar extends React.Component {

    renderShowDropdown() {
        return (
            <li className="nav-item dropdown">
                <a 
                    className="nav-link dropdown-toggle" 
                    data-toggle="dropdown"
                    href="#"
                >
                    Shows                      
                </a>
                <div className="dropdown-menu">
                    <a className="dropdown-item" href="/fan-of">Fan of</a>
                    <a className="dropdown-item" href="/show-new">New show</a>
                </div>
            </li>
        )
    }

    renderLeft() {
        return (
            <span>
                <li className="nav-item">
                    <a 
                        className="nav-link" 
                        href="/main"
                    >
                        Main
                    </a>
                </li>
                {this.renderShowDropdown()}
            </span>
        )
    }

    renderRight() {
        return (
            <div className="pull-xs-right">
                {this.renderUserMenu()}
                {this.renderNotAuthedMenu()}            
            </div>
        )
    }

    renderUserMenu() {
        if (!isAuthed())
            return;
        return (
            <li className="nav-item dropdown">
                <a 
                    className="nav-link dropdown-toggle" 
                    data-toggle="dropdown"
                    href="#"
                >
                    <i className="fa fa-user"></i>                      
                </a>
                <div className="dropdown-menu dropdown-menu-right">
                    <a className="dropdown-item" href="/account">Account</a>
                    <a className="dropdown-item" href="/account">Play servers</a>
                    <a className="dropdown-item" href="/sign-out">Sign out</a>
                </div>
            </li>
        )
    }

    renderNotAuthedMenu() {
        if (isAuthed()) 
            return;
        return (
            <span>
                <li className="nav-item">
                    <a 
                        className="nav-link" 
                        href="/create-user"
                    >
                        Create a user
                    </a>
                </li>
                <li className="nav-item">
                    <a 
                        className="nav-link" 
                        href="/sign-in"
                    >
                        Sign in
                    </a>
                </li>
            </span>
        )
    }

    render() {
        return (
            <nav className="navbar navbar-seplis">
                <div className="container">
                    <ul className="nav navbar-nav row">

                        <div className="col-xs-6 col-md-3">
                            {this.renderLeft()}
                        </div>

                        <div className="col-xs-6 col-md-3 col-md-push-6">
                            {this.renderRight()}
                        </div>
                        <div className="col-xs-12 col-md-6 col-md-pull-3">
                            <Search key="Search" />
                        </div>

                    </ul>
                </div>
            </nav>
        )
    }

}

export default Navbar;
