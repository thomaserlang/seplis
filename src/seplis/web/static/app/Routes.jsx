import React from 'react';
import {Router, Route, browserHistory, IndexRedirect} from 'react-router';

import Show from './views/show/Show';
import Main from './views/show/Main';
import Seasons from './views/show/Seasons';

import SignIn from './views/SignIn';

export default (
    <Router history={browserHistory}>
        <Route path="/show/:showId" component={Show}>
            <IndexRedirect to="/show/:showId/main" />
            <Route path="main" component={Main} />
            <Route path="info" component={SignIn} />
            <Route path="seasons" component={Seasons} />
        </Route>
    </Router>
);