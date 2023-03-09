// @ts-nocheck
import { Button } from '@chakra-ui/react';
import React from 'react';
import Chromecast from './Chromecast';

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
        this.onDeviceAvailable = this.deviceAvailable.bind(this);
        this.cast = new Chromecast();
        this.cast.load(this.onCastInit.bind(this));
        this.iconClick = this.castIconClick.bind(this);
    }

    componentWillUnmount() {
        this.cast.removeEventListener('isConnected', this.onConnected)
    }

    onCastInit() {
        this.cast.addEventListener('isConnected', this.onConnected);
        this.cast.addEventListener('isAvailable', this.onDeviceAvailable);
    }

    deviceAvailable(e) {
        this.setState({available: e.value});        
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
            <Button 
                mr="0.75rem"
                onClick={this.iconClick}
            >
                <img 
                    title="Chromecast"
                    className="castbutton"
                    src={icon}
                />
            </Button>
        );
    }
}

export default ChromecastIcon;