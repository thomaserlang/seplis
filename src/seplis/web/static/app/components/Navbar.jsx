import React from 'react'
import {Link} from 'react-router-dom'
import {request} from 'api'
import {isAuthed, getUserLevel} from 'utils'
import Search from './Search'
import ChromecastIcon from './player/ChromecastIcon'
import ChromecastBar from './player/ChromecastBar'

import './Navbar.scss'

class Navbar extends React.Component {

    renderShowDropdown() {
        return (
            <span className="dropdown">
                <a 
                    className="link dropdown-toggle" 
                    data-toggle="dropdown"
                >
                    Series
                </a>
                <div className="dropdown-menu">
                    <Link className="dropdown-item" to="/shows-main">Main</Link>
                    <Link className="dropdown-item" to="/air-dates">Air dates</Link>
                    <Link className="dropdown-item" to="/countdown">Countdown</Link>
                    <Link className="dropdown-item" to="/following">Following</Link>
                    <Link className="dropdown-item" to="/episodes-to-watch">Episodes to Watch</Link>
                    <Link className="dropdown-item" to="/recently-aired">Recently Aired</Link>
                    <Link className="dropdown-item" to="/shows-watched">Watched</Link>
                    <Link className="dropdown-item" to="/user-shows-stats">Stats</Link>
                    <div className="dropdown-divider"></div>
                    <Link className="dropdown-item" to="/show-new">New series</Link>
                </div>
            </span>
        )
    }

    renderMoviesDropdown() {
        return (
            <span className="dropdown">
                <a 
                    className="link dropdown-toggle" 
                    data-toggle="dropdown"
                >
                    Movies                   
                </a>
                <div className="dropdown-menu">
                    <Link className="dropdown-item" to="/movies-main">Main</Link>
                    <Link className="dropdown-item" to="/movies-stared">Stared</Link>
                    <Link className="dropdown-item" to="/movies-watched">Watched movies</Link>
                    <div className="dropdown-divider"></div>
                    <Link className="dropdown-item" to="/movie-new">New movie</Link>
                </div>
            </span>
        )
    }

    renderUserMenu() {
        if (!isAuthed())
            return
        return (
            <span className="dropdown">
                <a 
                    className="link dropdown-toggle" 
                    data-toggle="dropdown"
                >
                    <i className="fas fa-user"></i>                     
                </a>
                <div className="dropdown-menu dropdown-menu-right">
                    <Link className="dropdown-item" to="/account">Account</Link>
                    <Link className="dropdown-item" to="/play-servers">Play servers</Link>
                    <div className="dropdown-divider"></div>
                    <Link className="dropdown-item" to="/sign-out">Sign out</Link>
                </div>
            </span>
        )
    }

    renderChromecast() {
        if (!isAuthed())
            return
        return (               
            <span className="link">
                <ChromecastBar />
                <ChromecastIcon />
            </span>
        )    
    }

    renderSignIn() {
        if (isAuthed()) 
            return
        return (
            <Link 
                className="link" 
                to="/sign-in"
            >
                Sign in
            </Link>
        )
    }

    renderCreateUser() {
        if (isAuthed()) 
            return
        return (
            <Link 
                className="link" 
                to="/create-user"
            >
                Create user
            </Link>
        )
    }

    render() {
        return (
            <nav className="navbar-seplis">
                <div className="container">
                    <div className="row">
                        <div className="col-auto">
                            {this.renderShowDropdown()}
                            {this.renderMoviesDropdown()}
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

export default Navbar
