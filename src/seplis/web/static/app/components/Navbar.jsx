import React from 'react';
import {request} from 'api';
import {isAuthed, getUserLevel} from 'utils';
import Search from './Search';
import ChromecastIcon from './player/ChromecastIcon';
import ChromecastBar from './player/ChromecastBar';

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

    renderMain() {
        return (
            <li className="nav-item">
                <a 
                    className="nav-link" 
                    href="/main"
                >
                    Main
                </a>
            </li>
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
                    <a className="dropdown-item" href="/play-servers">Play servers</a>
                    <a className="dropdown-item" href="/sign-out">Sign out</a>
                </div>
            </li>
        )
    }

    renderChromecast() {
        if (!isAuthed())
            return;
        return (
            <li className="nav-item">                    
                <span
                    className="nav-link"
                    style={{
                        paddingBottom: 0,
                    }}
                >   <ChromecastBar />
                    <ChromecastIcon />
                </span>
            </li>
        )    
    }

    renderSignIn() {
        if (isAuthed()) 
            return;
        return (
            <li className="nav-item">
                <a 
                    className="nav-link" 
                    href="/sign-in"
                >
                    Sign in
                </a>
            </li>
        )
    }

    renderCreateUser() {
        if (isAuthed()) 
            return;
        return (
            <li className="nav-item">
                <a 
                    className="nav-link" 
                    href="/create-user"
                >
                    Create user
                </a>
            </li>
        )
    }

    render() {
        return (
            <nav className="navbar navbar-toggleable-xl navbar-seplis">
                <div className="container mr-auto mt-2 mt-lg-0">
                    <ul className="nav navbar-nav">
                        {this.renderMain()}
                        {this.renderShowDropdown()}

                        {this.renderChromecast()}
                        
                        {this.renderCreateUser()}
                        {this.renderSignIn()}
                        {this.renderUserMenu()}
                    </ul>
                </div>
            </nav>
        )
    }

}

export default Navbar;
