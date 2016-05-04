import './styles/Base.scss';
import './styles/Navbar.scss';
import './styles/FormBase.scss';
import './styles/Variables.scss';

import {apiClientSettings} from './api.jsx';

export default{
    React: require('react'),
    ReactDOM: require('react-dom'),
    seplis: {
        apiClientSettings: apiClientSettings,
        views: {
            Show: require('./views/Show.jsx'),
        }
    }
};