import './base.scss';
import {apiClientSettings} from './api.jsx';

export default{
    React: require('react'),
    ReactDOM: require('react-dom'),
    seplis: {
        apiClientSettings: apiClientSettings,
        WatchedButton: require('./components/shows/episodes/WatchedButton'),
        SeasonList: require('./components/shows/episodes/SeasonList'),
    }
};