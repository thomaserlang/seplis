import React from 'react';
import {Router, Route, browserHistory, IndexRoute} from 'react-router';

import Show from './views/show/Show';
import Main from './views/show/Main';

import SignIn from './views/SignIn';

export default (
    <Router history={browserHistory}>
        <Route path="/show/:showId" component={Show}>

            <Route path="main" component={Main} />
            <Route path="info" component={SignIn} />
        </Route>
    </Router>
);