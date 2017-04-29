import React from 'react';
import Chromecast from './Chromecast';

import './ChromecastIcon.scss';

class ChromecastIcon extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            connected: false,
            available: false,
        }
    }

    componentDidMount() {
        this.onConnected = this.connected.bind(this);
        this.cast = new Chromecast();
        this.cast.load(this.onCastInit.bind(this));
        this.iconClick = this.castIconClick.bind(this);
    }

    componentWillUnmount() {
        this.cast.removeEventListener('isConnected', this.onConnected)
    }

    onCastInit() {
        this.setState({available: true});
        this.cast.addEventListener('isConnected', this.onConnected);
    }

    connected(e) {
        this.setState({connected: e.value});
    }

    castIconClick(event) {
        this.cast.requestSession();
    }

    render() {
        if (!this.state.available)
            return null;
        let icon = '/static/img/chromecast.svg';
        if (this.state.connected)
            icon = '/static/img/chromecast_connected.svg';
        return (
            <img 
                onClick={this.iconClick}
                title="Chromecast"
                className="castbutton"
                src={icon}
            />
        );
    }
}

export default ChromecastIcon;