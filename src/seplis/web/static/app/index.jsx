import './styles/Base.scss';
import './styles/FormBase.scss';

import {apiClientSettings} from './api.jsx';
import Chromecast from 'components/player/Chromecast';

export default{
    React: require('react'),
    ReactDOM: require('react-dom'),
    $: require('jquery'),
    seplis: {
        Routes: require('./Routes.jsx'),
        apiClientSettings: apiClientSettings,
        Navbar: require('./components/Navbar.jsx'),
        Chromecast: Chromecast,
    }
};