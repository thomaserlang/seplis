import React from 'react';
import {Router, Route, browserHistory, IndexRedirect} from 'react-router';

import Show from './views/show/Show';
import ShowMain from './views/show/Main';
import ShowSeasons from './views/show/Seasons';
import ShowInfo from './views/show/Info';
import ShowEdit from './views/show/Edit';
import PlayEpisode from './views/show/PlayEpisode';

import ShowNew from './views/show/New';

import SignIn from './views/SignIn';
import CreateUser from './views/CreateUser';

import FanOf from './views/FanOf';
import RecentlyAired from './views/RecentlyAired';
import ShowsWatched from './views/ShowsWatched';
import Countdown from './views/Countdown';
import EpisodesToWatch from './views/EpisodesToWatch';
import Main from './views/Main';
import AirDates from './views/AirDates';
import Account from './views/Account';
import Password from './views/Password';
import PlayServers from './views/PlayServers';
import PlayServer from './views/PlayServer';

export default (
    <Router history={browserHistory}>
        <Route path="/sign-in" component={SignIn} />
        <Route path="/create-user" component={CreateUser} />
        <Route path="/show/:showId" component={Show}>
            <IndexRedirect to="/show/:showId/main" />
            <Route path="main" component={ShowMain} />
            <Route path="info" component={ShowInfo} />
            <Route path="seasons" component={ShowSeasons} />
            <Route path="edit" component={ShowEdit} />
        </Route>
        <Route path="/show/:showId/episode/:number/play" component={PlayEpisode} />
        <Route path="/show-new" component={ShowNew} />
        <Route path="/fan-of" component={FanOf} />
        <Route path="/recently-aired" component={RecentlyAired} />
        <Route path="/shows-watched" component={ShowsWatched} />
        <Route path="/countdown" component={Countdown} />
        <Route path="/episodes-to-watch" component={EpisodesToWatch} />
        <Route path="/main" component={Main} />
        <Route path="/air-dates" component={AirDates} />
        <Route path="/account" component={Account} />
        <Route path="/password" component={Password} />
        <Route path="/play-servers" component={PlayServers} />
        <Route path="/play-server" component={PlayServer} />
      </Router>
);