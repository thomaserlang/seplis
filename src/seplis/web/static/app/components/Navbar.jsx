import React from 'react';
import {request} from 'api';
import {isAuthed, getUserLevel} from 'utils';

import './Navbar.scss';

const navbarItemsLeft = [
    {
        name: 'Main',
        url: '/main',
        accessLevel: 0,
    },
    {
        name: 'Shows',
        items: [
            {
                name: 'Fan of',
                url: '/fan-of',
                accessLevel: 0,
            },
            {
                name: 'New show',
                url: '/show-new',
                accessLevel: 2,
            }
        ]
    }
]

class Navbar extends React.Component {

    renderItem(item) {
        if (('accessLevel' in item) && 
            (getUserLevel() < item.accessLevel))
            return;
        if ('items' in item) {
            return (                
                <li key={item.name} className="nav-item dropdown">
                    <a 
                        className="nav-link dropdown-toggle" 
                        data-toggle="dropdown"
                        href="#"
                    >
                        {item.name}                        
                    </a>
                    <div className="dropdown-menu">
                        {item.items.map((item, i) => (
                            <a key={item.name} className="dropdown-item" href={item.url}>
                                {item.name}
                            </a>
                        ))}
                    </div>
                </li>
            )
        }
        return (
            <li key={item.name} className="nav-item">
                <a href={item.url} className="nav-link">
                    {item.name}
                </a>
            </li>
        )
    }

    render() {
        return (
            <nav className="navbar navbar-seplis">
                <div className="container">
                    <ul className="nav navbar-nav">
                        {navbarItemsLeft.map((item, i) => (
                            this.renderItem(item)
                        ))}
                    </ul>
                </div>
            </nav>
        )
    }

}

export default Navbar;
