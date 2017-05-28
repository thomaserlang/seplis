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
            <span className="dropdown">
                <a 
                    className="link dropdown-toggle" 
                    data-toggle="dropdown"
                    href="#"
                >
                    Shows                      
                </a>
                <div className="dropdown-menu">
                    <a className="dropdown-item" href="/fan-of">Fan of</a>
                    <a className="dropdown-item" href="/show-new">New show</a>
                </div>
            </span>
        )
    }

    renderMain() {
        return (
            <a 
                className="link" 
                href="/main"
            >
                Main
            </a>
        )
    }

    renderAirDates() {
        return (
            <a 
                className="link" 
                href="/air-dates"
            >
                Air dates
            </a>
        )
    }

    renderUserMenu() {
        if (!isAuthed())
            return;
        return (
            <span className="dropdown">
                <a 
                    className="link dropdown-toggle" 
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
            </span>
        )
    }

    renderChromecast() {
        if (!isAuthed())
            return;
        return (               
            <span className="link">
                <ChromecastBar />
                <ChromecastIcon />
            </span>
        )    
    }

    renderSignIn() {
        if (isAuthed()) 
            return;
        return (
            <a 
                className="link" 
                href="/sign-in"
            >
                Sign in
            </a>
        )
    }

    renderCreateUser() {
        if (isAuthed()) 
            return;
        return (
            <a 
                className="link" 
                href="/create-user"
            >
                Create user
            </a>
        )
    }

    render() {
        return (
            <nav className="navbar-seplis">
                <div className="container">
                    <div className="row">
                        <div className="col-6 col-md-3">
                            {this.renderMain()}
                            {this.renderAirDates()}
                            {this.renderShowDropdown()}
                        </div>                        

                        <div className="col-6 col-md-3 push-md-6">
                            <div className="float-right">
                                {this.renderChromecast()}                            
                                {this.renderCreateUser()}
                                {this.renderSignIn()}
                                {this.renderUserMenu()}
                            </div>
                        </div>

                        <div className="col-12 col-md-6 pull-md-3">
                            <Search key="Search" />
                        </div>
                    </div>
                </div>
            </nav>
        )
    }

}

export default Navbar;
