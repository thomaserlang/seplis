import React from 'react';
import {Router, Route, browserHistory} from 'react-router';

import Show from './views/show/Show.jsx';

export default (
    <Router history={browserHistory}>
        <Route path="/show/:showId" component={Show}>
            <Route path="info" component={Show} />
        </Route>
    </Router>
);