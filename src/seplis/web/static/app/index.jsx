import './styles/Base.scss';
import './styles/FormBase.scss';

import {apiClientSettings} from './api.jsx';

export default{
    React: require('react'),
    ReactDOM: require('react-dom'),
    seplis: {
        Routes: require('./Routes.jsx'),
        apiClientSettings: apiClientSettings,
        Navbar: require('./components/Navbar.jsx'),
        views: {
            Show: require('./views/show/Show.jsx'),
            SignIn: require('./views/SignIn.jsx'),
        }
    }
};