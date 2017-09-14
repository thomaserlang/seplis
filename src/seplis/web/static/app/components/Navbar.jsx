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
                >
                    Shows                      
                </a>
                <div className="dropdown-menu">
                    <a className="dropdown-item" href="/fan-of">Fan of</a>
                    <a className="dropdown-item" href="/episodes-to-watch">Episodes to Watch</a>
                    <a className="dropdown-item" href="/recently-aired">Recently Aired</a>
                    <a className="dropdown-item" href="/recently-watched">Recently Watched</a>
                    <a className="dropdown-item" href="/countdown">Countdown</a>
                    <div className="dropdown-divider"></div>
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
                        <div className="col-auto">
                            {this.renderMain()}
                            {this.renderAirDates()}
                            {this.renderShowDropdown()}
                        </div>                        

                        <div className="col-auto ml-auto order-sm-2 order-md-12">
                            {this.renderChromecast()}                            
                            {this.renderCreateUser()}
                            {this.renderSignIn()}
                            {this.renderUserMenu()}
                        </div>

                        <div className="col-12 col-md-6 m-auto order-sm-12 order-md-2">
                            <Search key="Search" />
                        </div>
                    </div>
                </div>
            </nav>
        )
    }

}

export default Navbar;
