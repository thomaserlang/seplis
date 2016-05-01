import './styles/Base.scss';
import './styles/FormBase.scss';
import './styles/Variables.scss';

import {apiClientSettings} from './api.jsx';

export default{
    React: require('react'),
    ReactDOM: require('react-dom'),
    seplis: {
        apiClientSettings: apiClientSettings,
        SeasonList: require('./components/shows/episodes/SeasonList'),
        SignIn: require('./components/SignIn'),
        FanButton: require('./components/shows/FanButton'),
    }
};